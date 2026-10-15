# Draft and shop: Mite (#1) vs Univardisty of Shingtonwash (#2), 2026-10-15

Data: 108 team-games (101 matches, 54 per team, 6 per map) from `$S/ws/selected.json` + `$S/ws/steps/*.c.jsonl`.
Purchases are the `k=13` steps with `gold<0`; the exact items come from the `summary` line of each compact file
(`itemsBought`, `consumablesBought`, `earnedGold`, `spentGold`), so item identity is **measured**, not inferred.
Round-end `gold` in the summary is corrupt for some champions (values like 94489280602), so "unspent" uses the last
round snapshot. Scripts: `$S/reports/scripts_draft/{extract,draft,analyze_shop,trips,cons,extra}.py`.

Results today: Mite 34-20 (5-2 head-to-head vs Univardisty), Univardisty 26-28.

## 1. Draft

Map features (BFS spawn-to-spawn path, champions per team, camp gems/gold on the map):

| map | nch | path | altars | gems / gold | Mite draft (fixed, 6/6 games) | Mite W-L | Uni W-L |
|---|---|---|---|---|---|---|---|
| collision | 3 | 34 | 2 | 268 / 945 | Varg > Ryth > Cassi&Issac | 3-3 | 5-1 |
| packs | 3 | 26 | 6 | 180 / 610 | Ren > Stellar > Cassi&Issac | 5-1 | 3-3 |
| expanse | 3 | 85 | 10 | 614 / 1370 | Ren > Stellar > Cassi&Issac | 2-4 | 4-2 |
| interlock | 4 | 41 | 4 | 210 / 730 | Varg > Ryth > Cassi&Issac > Ren | 5-1 | 3-3 |
| rows | 4 | 73 | 2 | 646 / 1515 | Varg > Ryth > Cassi&Issac > Ren | 2-4 | 0-6 |
| corners | 5 | 40 | 5 | 496 / 1850 | Varg > Stellar > Cassi&Issac > Ryth > Ren | 3-3 | 0-6 |
| elkring | 5 | 31 | 2 | 180 / 975 | Varg > Stellar > Cassi&Issac > Ryth > Ren | 5-1 | 3-3 |
| monolith | 5 | 50 | 6 | 626 / 1375 | Varg > Stellar > Cassi&Issac > Ryth > Ren | 4-2 | 4-2 |
| lanes | 5 | 81 | 18 | 450 / 1395 | Varg > Stellar > Cassi&Issac > Tavi > Ren | 5-1 | 4-2 |

### Mite (measured)
- **One draft per map, identical in all 6 games of the map, regardless of opponent or side** (54/54). It is a lookup by map
  (or by champions-per-team): 3 picks -> {Varg,Ryth,C&I} on collision, {Ren,Stellar,C&I} on packs/expanse; 4 picks -> Varg,Ryth,C&I,Ren;
  5 picks -> Varg,Stellar,C&I,Ryth,Ren, with Tavi replacing Ryth only on lanes (the 18-altar, path-81 map).
- Champion pool is 6 champions: Cassi&Issac in all 54 games, Ren 48, Varg 42, Ryth 36, Stellar 36, Tavi 6. Never Prism, Marcella, Vendetta, Willow, Vesper.
- **First pick (= first to act every round) is Varg in 42/54, Ren in 12/54** (packs, expanse). Cassi&Issac is always 3rd. Ren is always last when present.
- No relation to path length or fight/farm beyond nch: the two long maps (expanse 85, lanes 81) get the same core as their nch group.

### Univardisty (measured; this changes the 2026-10-14 finding)
- The 5 games created at 06:55 UTC (vs Mite: corners, elkring, lanes, packs, rows) use exactly yesterday's fixed table
  (e.g. corners `265a46b9` Ryth>Stellar>Prism>Ren>Tavi, elkring `3e165d6b` Vesper>Stellar>Prism>Ren>Tavi, packs `e2e84b09` C&I>Stellar>Varg).
- **From 07:00 UTC on, the draft is no longer fixed per map**: 2-5 distinct drafts per map, differing even with the same map,
  same side and the same opponent picks visible (interlock side b: Ryth>C&I>Stellar>Ren 5x but C&I>Ren>Stellar>Tavi vs Mate in One `6cb958d0`;
  corners side a: Ren>Tavi>C&I>Marcella>Stellar vs Shawn `502126ec` and Ren>Marcella>Ryth>Varg>Tavi vs PTN `940529ee`).
  The variation is not explained by the opponent's revealed picks alone; it looks randomized or driven by opponent history (not decidable from replays).
- Stable cores: collision Stellar first (5/6) + Ren; expanse C&I>Vendetta>Varg (4/6); interlock Ryth>C&I>Stellar>Ren (5/6);
  monolith and rows always C&I first; lanes Ryth first (4/6) and Tavi always last; corners has Willow first in 3/6 (record 0-6 on corners).
- Pool is 11 champions (Stellar 41, Ren 34, C&I 33, Tavi 32, Varg 26, Ryth 22, Prism 13, Marcella 7, Vendetta 7, Willow 5, Vesper 2).
- Versus Mite the head-to-head went 2-5 for Univardisty; its two wins (collision `e9c3f66b` 1100-154 with Tavi>Stellar>Ren, monolith `ced08a2f`
  1018-768 with C&I>Stellar>Prism>Ren>Varg) came with the new drafting bot on side a.

### Mite vs Univardisty draft differences
- Mite: a fixed melee/farm core (Varg or Ryth first, C&I always) and at most 1-2 damage casters (Stellar, Ren). Uni: 3-4 casters
  (Stellar, Ren, Tavi, Prism) on 5-pick maps, melee (Varg, Vendetta, Marcella) on 3-pick farm maps.
- Mite's first pick is the splash farmer (Varg); Uni's first pick is usually C&I or Stellar.

## 2. Shop: what each champion buys

Shards cost 30 (bought in batches: a step of -90 = 3 shards, -150 = 5 shards = one emblem bought in one call). The only consumable seen
is slot 2 of `consumablesBought`, 10 gold; every use (`k=20`) happens within 2 tiles of an altar and never on spawn (Mite 167/167, Uni 248/248),
so slot 2 = **altar lock**. No teleport crystal (no 2-3 tile turn-start jumps after any purchase) and no other consumable was ever bought.

### Mite build order (measured from shard composition at every count; e.g. Varg with 6 shards = jungle 5 + durability 1, with 12 = durability 5 + jungle 5 + bruiser 2)

| type | games | 1st emblem | 2nd | 3rd | then | main stat |
|---|---|---|---|---|---|---|
| Varg | 42 | jungle strength x5 | durability strength x5 | bruiser health x5 | power strength, unlimited (up to 43 shards) | strength |
| Issac | 54 | jungle strength | durability strength (or power strength) | bruiser health | power strength | strength |
| Cassi | 54 | jungle focus | durability focus | bruiser health | power focus | focus |
| Stellar | 36 | jungle focus | durability focus | bruiser health | power focus | focus |
| Tavi | 6 | jungle focus | power focus | - | - | focus |
| Ryth | 36 | jungle (stat) | durability (stat) | bruiser health | power (stat) | **focus on 5-pick maps (corners, elkring, monolith), strength on collision/interlock/rows** |
| Ren | 48 | jungle (stat) | durability (stat) | bruiser health | power (stat) | **focus on corners/elkring/lanes/monolith, strength on expanse/interlock/packs/rows** |

- Order is sometimes jungle -> power -> durability (Issac 9 shards = jungle 5 + power 4 in 5 games) but jungle is always first.
- Validation by damage: Mite Varg in `ced08a2f` hits camps for 50 before r62, 75 after buying 5 strength shards at r62 (-150), 100 after r192 (5 more).
- Emblem passives obtained: jungle (-30% camp damage) first, durability (-10% damage) second, i.e. the farming champion is made safe at camps before anything else.
- Health is only ever the bruiser family (a 5-shard block after two main-stat emblems).

### Univardisty build order (measured)

| type | games | 1st emblem | 2nd | then |
|---|---|---|---|---|
| Stellar | 41 | power focus x5 | durability health x5 | power focus unlimited (up to 67) |
| Prism | 13 | power focus | durability health | power focus |
| Varg | 26 | power strength | durability health | power strength (up to 78) |
| Issac | 33 | power strength | durability health | power strength |
| Vendetta / Marcella / Vesper / Willow | 7/7/2/5 | power strength | durability health | power strength |
| Ryth | 22 | bruiser health | durability health | power strength |
| Ren | 34 | bruiser health | durability health | power focus (up to 71) |
| Cassi | 33 | bruiser health | durability focus | power focus |
| Tavi | 32 | treasure focus (field purchases, 82% of its buys) | durability focus | power focus (up to 87) |

- Uni never buys jungle or monster; Mite never buys power first, treasure, or health outside bruiser.
- Uni's stat choice does not change by map (Stellar always focus, Ryth/Ren always start health).

### Per-type shopping numbers (per champion-game; "trip" = one round with purchases)

| team | type | n | 1st buy round (med) | buys/g | trips/g | rounds between trips (med) | % bought dead | % on spawn | % field | gold earned | spent | altar locks/g |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Mite | Varg | 42 | 107 | 7.2 | 3.8 | 95 | 0 | 100 | 0 | 735 | 648 | 1.3 |
| Mite | Ryth | 36 | 95 | 7.5 | 4.4 | 90 | 0 | 100 | 0 | 806 | 738 | 1.1 |
| Mite | Ren | 48 | 78 | 7.7 | 4.2 | 75 | 0 | 100 | 0 | 708 | 649 | 1.3 |
| Mite | Issac | 54 | 69 | 6.7 | 4.1 | 72 | 0 | 100 | 0 | 603 | 545 | 1.2 |
| Mite | Stellar | 36 | 76 | 5.1 | 3.4 | 84 | 0 | 100 | 0 | 410 | 368 | 1.1 |
| Mite | Cassi | 54 | 172 | 3.9 | 2.5 | 90 | 0 | 100 | 0 | 318 | 296 | 0.8 |
| Mite | Tavi | 6 | 87 | 3.2 | 2.7 | 68 | 0 | 47 | 53 | 215 | 212 | 1.2 |
| Uni | Varg | 26 | 55 | 9.1 | 5.5 | 57 | 4 | 96 | 0 | 1136 | 1070 | 2.2 |
| Uni | Ren | 34 | 73 | 8.6 | 5.9 | 73 | 10 | 90 | 0 | 792 | 756 | 2.6 |
| Uni | Issac | 33 | 96 | 5.2 | 3.8 | 66 | 6 | 94 | 0 | 607 | 555 | 1.3 |
| Uni | Stellar | 41 | 138 | 5.8 | 3.7 | 94 | 21 | 79 | 0 | 504 | 461 | 1.6 |
| Uni | Tavi | 32 | 122 | 7.1 | 6.2 | 42 | 7 | 11 | 82 | 600 | 590 | 1.0 |
| Uni | Ryth | 22 | 64 | 6.7 | 4.3 | 87 | 16 | 84 | 0 | 513 | 473 | 2.3 |
| Uni | Prism | 13 | 98 | 5.0 | 3.7 | 71 | 6 | 94 | 0 | 485 | 437 | 1.5 |
| Uni | Cassi | 33 | 228 | 2.7 | 2.0 | 104 | 6 | 94 | 0 | 223 | 200 | 0.9 |

Example sequences (round:gold, `hp+` = health shards, `[dead]`, `[field]`):
- Mite Ryth, collision `e9c3f66b` (loss): r63 -90 | r195 -60,-30 | r334 -120,-60(hp+200) | r434 -90(hp+300): 5 durability str, 5 jungle str, 5 bruiser hp; earned 540, spent 450, 90 left at end.
- Mite Varg, monolith `ced08a2f` (loss): r62 -150,-10 | r192 -150,-120(hp+400) | r299 -30(hp+100),-240 | r422 -90: jungle 5, durability 5, bruiser 5, power 11 (all strength); earned 790 = spent 790.
- Uni Stellar, collision `e9c3f66b` (win 1100-154): r81 -10(lock),-150,-30(hp+75) | r135 -120(hp+300),-90 | r238 -10,-210 | r303 -10,-180 | r340 -180 | r411 -270 | r476 -180: power focus 42, durability health 5; earned 1445, spent 1440, 5 left.
- Uni Tavi, same game: 18 field purchases from r84 to r498 (never returns to spawn except for the lock at r139): treasure 5, durability 5, power focus 32.
- Uni Ren, corners `265a46b9` (loss): r188 -10,-90(hp+300) | r365 -30(hp+100): only 4 bruiser health shards in 805 rounds (earned 150) - the corners losses are gold-starved, not shop-starved.

## 3. Timing of shopping trips

| measure | Mite | Uni |
|---|---|---|
| recall arrivals (non-Tavi) | 1267 | 928 |
| ... followed by a purchase within 2 rounds | 66% | 70% |
| arrivals with hp >= 70% ("shopping/teleport" recalls) | 372 (29%) | 244 (26%) |
| ... of which with a purchase | 296 (80%) | 233 (95%) |
| gold carried on a hp>=70% recall arrival (median; share >= 90) | 180; 79% | 200; 94% |
| gold carried on a hp<70% recall arrival (median; share >= 90) | 90; 50% | 62; 46% |
| rounds staying on spawn after a hp>=70% arrival (median) | 3 | 4 |
| rounds alive on spawn per champion-game (median) | 17 | 17 |
| purchases made while dead | 0 / 1698 (0%) | 140 / 1357 (10%); 35% of deaths are followed by a purchase 0-1 rounds after dying |
| first purchase before any recall or death | 3 / 252 | 23 / 226 |
| gold left after a shopping round (median; share exactly 0; share < 30) | 0; 60%; 100% | 10; 17%; 100% |
| shards per buy step (1/2/3/4/5/6+) | 313/228/289/172/255/152 | 179/228/175/95/194/293 |
| gold earned per game (median) / per round | 2905 / 6.09 | 3088 / 5.04 |
| spent per game (median) | 2770 | 2860 |
| unspent at game end (median per game; % of earned) | 238 (9%) | 130 (6%) |

- Both teams **recall to shop**: a quarter of all recalls arrive at >= 70% hp, carrying 180-200 gold (Uni 94% carry >= 90), buy, and leave after 3-4 rounds.
  Low-hp recalls are heal trips that shop with whatever gold is there (half carry >= 90).
- Mite buys only when alive on spawn (never while dead, 0/1698); Uni uses the dead turn immediately (dead purchases at 0-1 rounds after death) and
  sometimes only there (Uni Stellar: 21% of its purchases dead).
- Uni buys the altar lock (10 g) first in the shopping round, then shards (`r81 -10, -150, -30`), and leaves 10 gold more often than Mite; both always drop below 30 gold, i.e. **nobody saves gold**.
- Rounds between trips: Mite 72-95 per type, Uni 42-94 (Tavi 42 because it shops in the field).
- Map economy per game (earned/spent/emblems): Mite out-earns Uni on lanes (1673 vs 613), interlock (2642 vs 1404), corners (1067 vs 907);
  Uni out-earns Mite on collision (4020 vs 3298), monolith (4327 vs 4077) and rows (4246 vs 4193). On the two maps Uni went 0-6 (corners, rows)
  it averaged 2.7 and 24.3 emblems/game respectively, so rows losses are not about items; corners losses are about never getting gold (907/game over 707 rounds).

## 4. Comparison and relation to results

- Draft: Mite = fixed table keyed by map (first pick Varg, C&I always), 34-20. Uni = new randomized/adaptive drafter since 07:00, 26-28, 0-6 on corners
  and rows, 2-5 on the maps where it changed drafts most. Its best map today (collision 5-1) is also its most stable draft (Stellar + Ren in 6/6).
- Shop: Mite's build is a **farming-safety build** (jungle -> durability -> bruiser health -> power) with the main stat chosen per champion and, for Ryth/Ren,
  per map (focus on 5-pick fight maps, strength on 3-4-pick maps). Uni's build is a **raw-stat build** (power x5 -> durability health x5 -> power forever;
  tanks start with bruiser health; Tavi starts with treasure). Both spend everything they have at every visit and never buy teleport crystals.
- Mite wins the gold race on the small/medium maps (6.09 vs 5.04 gold per round over all games) and had no dead-shopping; Uni compensates by shopping while dead and by
  Tavi's field purchases (82% of Tavi's buys, median 42 rounds between trips).
- Head-to-head: Mite 5-2. In the 2 Uni wins, Uni's Stellar/Tavi reached 42 and 32 power-focus shards (collision `e9c3f66b`) and Issac 34 power-strength (monolith `ced08a2f`),
  far above Mite's deepest stack in those games (11 power shards).

## Rules they seem to follow

Mite (measured unless marked):
1. Draft = fixed list per map (54/54): 3 picks Varg,Ryth,C&I (collision) or Ren,Stellar,C&I (packs, expanse); 4 picks Varg,Ryth,C&I,Ren; 5 picks Varg,Stellar,C&I,Ryth,Ren (Tavi for Ryth on lanes). Varg (or Ren) acts first.
2. Shop only when alive on spawn (0 dead purchases), spend down to < 30 gold every time (100%), 60% to exactly 0; buy in batches of 3 (-90) or 5 (-150) shards when the gold allows.
3. Build: jungle(main stat) x5 -> durability(main) x5 -> bruiser health x5 -> power(main) without limit. Main stat: strength for Varg/Issac, focus for Cassi/Stellar/Tavi; Ryth and Ren focus on 5-pick maps, strength otherwise (inferred rule, 100% consistent over 84 games).
4. Recall to shop once ~180 gold is carried (79% of high-hp recalls carry >= 90), stay 3 rounds, leave (inferred threshold; measured medians).
5. Buy one altar lock (10 g) about every other trip (1.1-1.3 per champion-game) and place it next to a contested altar; no other consumables.

Univardisty (measured unless marked):
1. Draft is no longer fixed: since 07:00 UTC it varies within the same map/side/opponent-info (mechanism not decidable from replays). Before 07:00 it was yesterday's table.
2. Build: power(main) x5 -> durability health x5 -> power(main) forever (Stellar, Prism, Varg, Issac, Vendetta, Marcella, Vesper, Willow); bruiser health x5 first for Ryth/Ren/Cassi; treasure focus x5 first for Tavi, who buys in the field.
3. Shops at the first dead turn (35% of deaths, 0-1 rounds after dying) and on every spawn visit; buys the altar lock first, then shards; leaves 10 gold or less (median 10, 100% < 30).
4. Recalls at >= 70% hp are shopping trips (95% buy; median 200 gold carried), 4 rounds on spawn.
5. 1.6-2.6 altar locks per game for Stellar/Ren/Ryth/Varg; no teleport crystals.
