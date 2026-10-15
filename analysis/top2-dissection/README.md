# How the #1 (Mite) and #2 (Univardisty of Shingtonwash) decide, dissected

15-10-2026. Ladder at 08:22 UTC: Mite 1834 (#1), Univardisty 1816 (#2). This is a decision-by-decision dissection of their play, built on the 101 games (108 team-games, 6 per team per map, each against a different top-20 rival, 07:00-08:28 UTC) that the "Read the map, find the cycle" study already gathered. That study covered the farming camp set, the nearest-camp rule and recall as a teleport; this one covers everything else. Every game was re-decoded step by step (every move, hit, cast, purchase, channel), and six analyses ran in parallel. The six detailed reports, with tables, thresholds and example rounds, are in this folder:

| report | what it covers |
|---|---|
| `draft_shop.md` | draft per map and per opponent, shop order and timing, items, gold economy |
| `opening.md` | rounds 0-60: who goes where, first camp, first capture, first tribute, first contact, per-map timelines |
| `fights.md` | when they engage and disengage, hp thresholds, chase, positioning, kiting, formation, grouping, outcomes per map/opponent |
| `targeting_spells.md` | target choice on champions and camps, every spell slot's use, cast distance, turn order, kills |
| `map_control.md` | territory over time, middle camps and steals, altars, reaction to the opponent, score state, per-opponent divergence |
| `recall_survival.md` | every recall by reason, recall safety, spawn time, tribute decisions, deaths and whether they were avoidable, respawn |

Scripts are in `scripts_*/`; the decoded games (`ws/steps/<match>.c.jsonl`) and their format (`DATA.md`) are in `data/`. "Measured" below means read from the events; "inferred" means consistent with the numbers but the exact condition is not observable.

Results today: Mite 34-20, Univardisty 26-28 (0-6 on corners and rows). Head to head Mite 5-2.

## 1. The two bots in one paragraph each

**Mite** is a fixed-script farm bot with an hp-first survival rule. Same draft on a map against everyone (54/54), same opening path until an enemy is in vision, whole team stacked on the nearest camp, one champion left on the tiles to capture, small bags banked at the nearest altar on every pass (22 tributes a game, median 36 gems), recall the moment hp drops under 50% wherever the enemy is, shop only on spawn with a farming-safety build (jungle, durability, bruiser health, then power), fight close (casts from 3 tiles, melee wall in front, tight clump), never chase, never raid the enemy half. It wins by losing less: 4.9 deaths a game, 5.7% of its tributed gems lost to deaths, 6.1 gold per round.

**Univardisty** is a ranged caster bot that fights for the map. Draft now changes from game to game (2-5 drafts per map since 07:00 UTC, mechanism not decidable from replays), pre-assigned split from round 1 (3 on the nearest camp, 1-2 straight to a second camp or the centre), casters shoot from the edge of range (4, area spells reaching 5), bigger bags (median 44, p90 96), raids enemy gem clusters on lanes, recall only when no enemy is in vision (self-cancels and walks a tile if one appears), shops while dead, raw-stat build (power x5, durability health x5, power forever). It does 50% more champion damage than Mite (15.5k vs 10.2k a game, 76% from spells) but dies more (6.1 a game) and loses twice the gems to deaths (12.6% of what it tributes).

## 2. Decision by decision

### Draft (measured)
- Mite, by champions per team: 3 picks = Varg, Ryth, Cassi&Issac on collision, Ren, Stellar, Cassi&Issac on packs/expanse; 4 picks = Varg, Ryth, C&I, Ren; 5 picks = Varg, Stellar, C&I, Ryth, Ren (Tavi for Ryth on lanes). Varg (or Ren) picks first and so acts first every round; C&I always third. Pool of 6 champions, never Prism/Vendetta/Willow/Marcella/Vesper.
- Univardisty before 07:00 UTC used yesterday's fixed table; from 07:00 it varies even with the same map, side and visible opponent picks (interlock side b: Ryth>C&I>Stellar>Ren 5 times, C&I>Ren>Stellar>Tavi once). Stable cores: Stellar+Ren on collision (5-1, its best map), C&I first on monolith/rows, Tavi last on lanes; Willow first in 3 of 6 corners games (0-6).
- The audit thread's point stands: a caster draft is not the edge by itself. Mite drafts 1-2 casters and still wins the middle on collision/packs/interlock; Univardisty's caster line went 0-6 on corners today.

### Shop (measured)
- Nobody saves gold: every shopping round ends below 30 gold (Mite at exactly 0 in 60% of them). Shards are bought in batches of 3 or 5 (one emblem in one call).
- Mite build, every champion: jungle (main stat) x5, durability (main) x5, bruiser health x5, then power (main) without limit. Main stat = strength for Varg/Issac, focus for Cassi/Stellar/Tavi; Ryth and Ren take focus on 5-pick maps and strength on 3-4-pick maps (100% consistent over 84 champion-games). Validated by damage: Varg's camp hit goes 50 -> 75 -> 100 as the strength emblems land (`ced08a2f` r62, r192).
- Univardisty build: power (main) x5, durability health x5, power forever for Stellar/Prism/Varg/Issac/Vendetta/Marcella; bruiser health first for Ryth/Ren/Cassi; Tavi starts treasure focus and buys 82% of its items in the field. Never jungle, never monster.
- Timing: first purchase at r69-107 (Mite) / r55-138 (Uni) depending on champion; a shopping trip every 72-95 rounds (Mite), 42-94 (Uni). About a quarter of all recalls are shopping trips: arrive at 70%+ hp with 180-200 gold, buy, leave after 3-4 rounds. Mite buys only alive on spawn (0 of 1698 purchases while dead); Univardisty buys on the first dead turn after 35% of its deaths.
- The only consumable is the altar lock (10 gold): placed within 2 tiles of an altar right before the team's own tribute (step k20 then k12, e.g. `e9c3f66b` r65 Ren), Mite 1.1-1.3 per champion-game, Univardisty 1.6-2.6 for Stellar/Ren/Ryth/Varg. No teleport crystals. Example of a lock deciding a game: `1c547a16` (collision, 2000 rounds): hello locks the altar at r988 and Univardisty does not tribute again until r1959, walking around with 100-476 gems per champion; it still won 922-462.
- Economy: Mite 6.09 gold/round vs 5.04; Mite out-earns on lanes (1673 vs 613 a game), interlock, corners; Univardisty on collision, monolith, rows.

### Opening (measured; see `opening.md` for the per-map timelines)
- Mite: the whole team stacks the nearest camp (first hit r2-10, dead in 4-11 rounds, 16 on rows' 3-wolf pack), exactly one champion stays on the capture tiles (reward lands kill+6 rounds in every game), everybody else leaves that round for the next-nearest camp with 1-3 per camp. Planned exceptions: Varg walks alone to a far elk on lanes/elkring, Stellar alone to the gem cluster on expanse, and on corners 4 champions go straight to the centre altar (arrive r17-25) while Issac+Ren take the wolf.
- Univardisty: split from round 1 (3 on the nearest camp, 1-2 to a second camp or the centre: monolith Stellar to wolf d9, interlock Issac to the centre r17, corners 3 casters to the centre clusters r15-17); casters shoot the first camp from range 3-5 at r1-3; kills take 9-10 rounds with 3 hitters, 15 with 2, 19 with 1.
- First tribute: Mite r25-32 on 6 of 9 maps with a 22-44 bag, at the middle altar on fight maps; Univardisty r50-67 or later, carrying 100-150 gems at r60, and recall-shops right after the first capture (r21-31).
- Fight maps: Mite farms 2-3 camps before the middle (collision: Issac at the centre altar r25 with 22 gems; interlock: first contact r37-43 after 3 captures, 0 deaths in all 6 first fights). Univardisty won all 6 collision first fights (arrives r38-42) and lost 3-5 champions in the first corners fight in 4 of 6 games.
- Determinism: a team's games on a map are identical until an enemy is within ~10 tiles (corners r18, packs r26, collision r30-38, monolith r92; rows identical for 369 rounds). Nothing the opponent does changes the opening except being seen.
- Mite's one opening leak: a lone champion hitting an elk for 10-30 rounds without killing it, then recalling empty (elkring Varg r20-49, corners Issac r22-30, interlock Issac r41-52).

### Engaging a fight (measured)
- The opener is a spell at 4-5 tiles in 87-91% of fights (Mite: Ryth's area stun 37%, then Stellar/Cassi; Uni: Stellar at 5, Ren/Tavi stun at 4). They walk into range to do it (moved in each of the 3 previous rounds 58-72%); only 8-10% of openers come from a champion that stood and waited.
- They do not wait for an advantage. Numbers: Mite opens with a local edge 43% of the time, Univardisty opens outnumbered 54% of the time. Hp: equal (89 vs 89, 84 vs 88). Low enemies: only 8-12% of first victims are under 50% hp (22% of enemies in vision are).
- They do pick the victim: isolated (no ally within 4) 60% / 48% vs 35% / 26% baseline; Univardisty also hits camp-busy enemies (17%, its best fights at 1.20 kills / 0.57 deaths) and recalling ones (13%).
- Hitting first is what pays: 0.74 kills / 0.5 deaths per real fight when they open, 0.55-0.59 / 0.8-0.9 when the enemy opens. Both hit first 54-55% of the time.
- Today both were only even in fights (Mite 0.67/0.68 kills/deaths per real fight, Uni 0.66/0.61), well below yesterday's Univardisty numbers; corners is the bloodbath (2000+ damage per fight, Uni 0-6) and collision is Univardisty's map (93 kills to 32).
- Nobody chases: median 0 follow steps, 3+ steps in 12-13%. A lone Mite melee does not engage casters it outnumbers without a spell ready.

### Leaving a fight and surviving (measured)
- Mite leaves on hp: first step away under fire at 38% median (69% below 50%), walks toward spawn until the nearest enemy is 7 tiles away and recalls (93% completion from 7+). Univardisty leaves on numbers: 52% of its retreats happen while outnumbered, at 47% hp median; above 70% hp it is a kite (back in within 8 rounds); it recalls at 9-10 tiles.
- Retreating works: 80-84% survive the next 12 rounds. 70% of deaths are champions that stayed; Mite dies in bursts (40% go from 50%+ hp to dead in 2 rounds, Stellar spell 700 on Cassi `e9c3f66b` r54), Univardisty dies slowly and outnumbered (43%), 25% of its deaths had a clear walk/recall window at <50% hp with no enemy within 3 that it spent fighting.
- Recall rule, both teams: heal recall only below 50% hp (max 49% over 716 + 575 heal recalls, every champion). Mite starts it even with an enemy at 7-8 tiles (35% of starts) and retries every round when interrupted (Issac `d1a5da76` r478-505: 27 attempts while a wolf hits it; 44 recalls interrupted by camps, a bug). Univardisty starts it only with nobody in vision (74% at 9+ tiles, 0.3% interrupted there) and self-cancels by walking a tile when an enemy appears (68 times).
- Recall reasons (arrivals): heal 56-57%, shop 25% / 13%, reposition at full hp 14% / 17%, bank 3.5% / 8% (only where an altar is within 10 of spawn: rows, lanes, packs), escape 1.4% / 5%. Spawn stay is 1 or 4 rounds, everyone heals to full before leaving. Cost: Mite 9.4% of champion-rounds in recall or on spawn (25 starts a game), Univardisty 6.9% (20).
- There is no healing outside spawn (every regen event in 101 games is on a spawn tile) and no potions: above 50% they keep farming or fighting at that hp.
- Deaths per game: Mite 4.9 (corners 16, collision 7.5, elkring 7.3, interlock 5.5, farm maps 0-1.7), Univardisty 6.1 (corners 16.5, interlock 10.3, elkring 9.8). Spells are 60-62% of killing blows; Stellar is the top killer of both. Camp deaths: 4 vs 14 (9 on elkring, contested wolf packs), always with enemies around.

### Targeting (measured)
- With 2+ enemies in range both finish a killable target first (88-89%) and stick to the current target (78-81%). Then Mite goes nearest (beats lowest-hp 59:40), Univardisty goes lowest absolute hp (beats nearest 56:35). Best rule found: Mite "killable > nearest > lowest hp%" (76% of decisions), Univardisty "killable > keep target > lowest hp" (73%). Neither hits casters first or gem carriers as such.
- Focus: all of a round's damage lands on one victim in 92% of rounds; with 2+ attackers all hit the same one 66% / 63%. Switches (11-14%) are because the target left range (half) or died (a fifth).
- Camps: open on the elk (Mite 150:25, Uni 134:38), everyone on the same monster (90% / 84%), ranged attack from exactly 3 tiles (86-97%), the first hitter (melee in 76-81% of mixed groups) takes the aggro. Univardisty farms solo 71% of the time. Mite's Cassi stuns the awake elk on cooldown (198 of 204 camp stuns) and the elk never attacks the next round.
- No last-hit arrangement: allies in range hit the dying enemy 31/36 and 15/18 times; kills go to the biggest hit, i.e. the caster line (59% / 65%).

### Spells (measured)
- Nobody saves a spell: damage and stun spells go out whenever an enemy champion is within 4 and the slot is up (Mite 0.76-0.88 of such turns, Uni 0.55-0.88; the misses are walking turns, since exclusive spells are never cast after a step, 0 of 11k casts). Only 6-13% of stun casts kill; 34-39% land on a target walking away.
- Cast distance: Mite from 3 (Cassi 73%, Stellar 72%: basic-attack range), Univardisty from 4 (55-61%) with area spells placed so the splash reaches 5 (Stellar 49%, Ryth 39%).
- Stellar/Prism: single target by default, area when 2+ enemies sit within radius 1 of one tile (Mite 7 of 9, Uni 11 of 12); otherwise the slots alternate on cooldown. Area casts hit 2+ champions 21-29% of the time (Ryth stun on 4 at `bf3fc10f` r54).
- On camps: Cassi/Tavi spells on cooldown on any monster (0.93-1.00); Ren/Ryth stun and Varg shield only on an awake monster (0.71-0.96 vs 0.02-0.33 asleep). Stellar does 77-81% of its camp damage with spells.
- Attack resets: a farming tool (82-99% double-hit a monster). Univardisty's Tavi/Willow/Vesper use the reset to walk and still shoot (48-67% of their resets); Mite 4%. Dashes: travel with the walk (94-99.7%); Mite's Issac/Ren dash-then-hit (214 turns), Univardisty's melee dash only to leave (0 dash-then-hit). Varg shield: Mite as a farm buffer vs awake monsters (0.79 vs 0.02 asleep), Uni as a fight buffer under 50% hp.
- Spell share of champion damage: Mite 62% of 10.2k a game, Univardisty 76% of 15.5k (Stellar+Tavi+Ren = 70% of its damage).

### Positioning and formation (measured)
- Casters sit at 4-5 from the nearest enemy (Stellar 5 = AoE edge, Cassi 4, Tavi/Willow 3); melee spend more fight rounds at 3-5 than adjacent (13-14% at 1).
- Mite: melee strictly in front of every caster in 66% of rounds (gap 1.35 tiles), tight clump (max pairwise 4, nearest ally adjacent 39%), ranged stand and hit twice (Cassi double attack 36%). Univardisty: spread (41% of rounds with max pairwise 6+), melee only marginally in front (52%), ranged alternate hit and step back/sideways (40-55% after an attack).
- No bush or hole use in fights; no regrouping before engaging (they converge from 9 to 6 tiles apart on the way in; Uni's opening caster has no ally nearby 38% of the time).

### Map control and reacting to the opponent (measured)
- Both farm their own half and drift to the middle as the nearest camps that are up move there (own-half share 88% -> 73% Mite, 86% -> 71% Uni). The enemy half: Mite 2-6% of champion-rounds, Uni 4-9%. 94% / 88% of crossings are chases of a visible enemy (median 10 rounds); "enemy dead" is never the trigger.
- Enemy-side captures: Mite 0.3 a game, only while already fighting there; Univardisty 1.3 a game, 34 of them raids of enemy gem clusters on lanes from r~80 at any score (`0c9cfa11` r269-351: 7 enemy clusters in a row while -114, won 1004-944).
- Middle camps: Mite wins them on collision 54-30, packs 63-23, interlock 25-3; Univardisty loses corners 45-129. Steals (capture without the last hit, 124 in 101 games) are the by-product of winning the fight over a cleared group, not of hiding (`265a46b9` r24-31).
- On sight of an enemy: keep the current job (57-58% keep hitting the camp) and close in (~50%). The only retreat trigger is hp under 50% (Mite recalls 40%, Uni walks away 32%). Carrying gems changes nothing (Mite with 50+ gems approaches 59%). No territorial defence: an enemy group in their half does not pull champions in (2.6 -> 2.1 nearby after 10 rounds). After an ally's death 61-62% of the others keep attacking; only the low-hp ones leave.
- Score: nobody plays safe when ahead; ahead = more forward and more damage (Uni 39% of champion-rounds in mid/enemy, 1318 damage per 100 champion-rounds). Behind = fewer captures and half the tribute rate because champions are dead or far. Last 100 rounds: tribute rate x1.5-2 with normal bags.
- Tribute: on every altar pass, instantly (95% / 97%), at the altar nearest the camp just cleared; never bags of 10 or less; bag median 36 / 44, p90 70 / 96 (rows 132 / 99).
- Vision: by moving as a pack; wards cannot be seen in replays; no bush lookouts.

## 3. Where Mite and Univardisty differ (and which side wins)

| decision | Mite | Univardisty | who it favours |
|---|---|---|---|
| draft | fixed per map | varies per game | Mite today (0-6 corners/rows for Uni) |
| build | jungle, durability, bruiser hp, power | power, durability hp, power | Uni in long fights (Stellar 42 power shards in its collision win) |
| opening | stack one camp, 4-11 rounds | split 3+2, 9-19 rounds | Mite: first tribute r25-32 vs r50-67 |
| banking | small bags on every pass, 22/game | bigger bags, 16/game | Mite: 5.7% vs 12.6% of gems lost to deaths |
| recall | hp < 50%, from 7 tiles, retries under fire | hp < 50% only when unseen, self-cancels | Mite fewer deaths, Uni fewer rounds lost |
| engage | Ryth stun at 4-5, 43% ahead in numbers | Stellar at 5, 54% outnumbered, enemy half | even today |
| cast distance | 3 | 4-5 | Uni (55% of the damage trade) |
| targeting | nearest, then hp% | keep target, then lowest hp | both ~75% |
| formation | clump, melee wall 66% | spread, kiting ranged | neither measurable |
| enemy half | never, except chases | raids gem clusters on lanes | Uni on lanes/monolith |
| shop | only alive on spawn | also while dead; Tavi in the field | Uni (10% of its buys are dead turns) |
| spell share of damage | 62% of 10.2k | 76% of 15.5k | Uni |

Mite beat Univardisty 5-2 today with less damage and fewer kills: its edge is dying less and losing fewer gems, not fighting better. Univardisty's wins (collision `e9c3f66b` 1100-154, monolith `ced08a2f`) came where its caster line could farm Mite's melee walking into the middle wolf under three casters (r44-54, repeated: 19 Mite deaths).

## 4. What is still unknown or inferred
- Univardisty's draft mechanism since 07:00 (random, history-based or something not visible in replays).
- Wards: not exported by the replay decoder; two effect-less action kinds exist and at most one of them is the ward.
- The 4-round spawn stays and the 1-tile path tie-breaks that differ between otherwise identical games (probably time-budget dependent code).
- Why Mite's lone champion attacks an elk it cannot kill; why its recall retries under camp fire.
