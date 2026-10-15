# Fight engagement, disengagement, positioning and formation: Mite (#1) and Univardisty of Shingtonwash (#2)

Data: 108 team-records (101 matches, 2026-10-15), compact replays in `$S/ws/steps`. Scripts in `$S/reports/scripts_fights/`
(`common.py` loader, `fights_build.py` -> `fights.json`, `analyze_fights.py`, `positioning.py`, `engage_detail.py`, `retreat_detail.py`,
`timeline.py <match-prefix> <mite|uni> <r0> <r1>` prints a round-by-round fight). Raw outputs: `out_*.txt` next to the scripts.

**Fight** = cluster of champion-on-champion hits merged when within 5 rounds and 8 tiles (union-find). "Real" fight = >= 1000 total damage or a death.
"Present" = alive within 8 tiles of the first victim at the snapshot before the first hit. All distances are Chebyshev; "dist 5" for a spell means a
radius-1 ground spell (Ryth stun, Stellar/Prism AoE) placed at range 4 whose edge reached a target 5 away. 1659 fights (702 Mite, 957 Uni; Mite-vs-Uni games counted once per team).

## 0. Headline numbers

| | Mite | Univardisty |
|---|---|---|
| fights / real fights | 702 / 389 | 957 / 526 |
| hit first (real fights) | 54% | 55% |
| kills / deaths per real fight | 0.67 / 0.68 | 0.66 / 0.61 |
| damage dealt / taken per real fight | 1260 / 1300 | 1413 / 1178 |
| share of damage that is ours (all fights) | 49% | 55% |
| opener is a spell | 87% | 91% |
| opener distance 4-5 (spell range) | 78% | 79% |
| first victim isolated (no ally within 4) | 60% (baseline 35%) | 48% (baseline 26%) |
| real fights in own half / middle / enemy half | 42 / 27 / 31% | 29 / 25 / 46% |
| first step away under fire: hp% median | 38% | 47% |
| recall under threat: hp% median, distance to nearest enemy median | 33%, 7 | 29%, 8 |
| recall completed when enemy within 10 | 87% | 76% |
| retreating champion dies anyway (under fire) | 16% | 20% |
| chase a retreating enemy >= 3 steps | 12% | 13% |
| melee is the front body (rounds with both classes) | 74% | 58% |

Against today's top-20 rivals, both teams are roughly even in fights (K/D ~1.0): their ladder edge today came less from fight dominance than yesterday's
Univardisty numbers (1.27/0.36) suggested. Univardisty still wins the damage trade (55% of damage), Mite does not (49%).

## 1. ENGAGE: when do they start a fight

Conditions at the moment of the first hit (real fights), split by who hit first:

| team | who hit first | n | our n vs their n (within 8) | we outnumber / equal / outnumbered | our hp% / their hp% (med) | we healthier (+5) | our / their dist to own spawn (med) | they busy with camp | K/D in those fights |
|---|---|---|---|---|---|---|---|---|---|
| Mite | us | 210 | 2.96 vs 2.76 | 43 / 28 / 29% | 89 / 89 | 35% | 15 / 14 | 30% | 0.74 / 0.52 |
| Mite | them | 179 | 3.08 vs 2.73 | 45 / 28 / 27% | 89 / 87 | 39% | 12 / 16 | 25% | 0.59 / 0.87 |
| Uni | us | 288 | 2.47 vs 3.06 | 22 / 24 / 54% | 84 / 88 | 35% | 18 / 14 | 34% | 0.74 / 0.46 |
| Uni | them | 238 | 2.61 vs 3.06 | 21 / 32 / 47% | 82 / 86 | 28% | 16 / 15 | 31% | 0.55 / 0.79 |

What the numbers say:

- **Hitting first is what matters, not the pre-conditions.** Both teams: K/D 0.74/0.5 when they open, 0.55-0.59/0.8-0.9 when the enemy opens.
- **They do not wait for a numbers advantage.** Mite opens with a local advantage only 43% of the time; Uni opens *outnumbered* 54% of the time
  (partly structural: Uni drafts 5 bodies where Mite/VeryGood field 6, and Uni fights in the enemy half). Counting only champions within 5 tiles,
  the share of fights where they hit first is *highest when behind in numbers* (Mite 69-78%, Uni 65-92% per map) and lowest when ahead (29-59%):
  the typical opener is a range-4/5 spell poke on the first enemy that walks into range, before the groups have merged.
- **They do not wait to be healthier**: our hp% ~ their hp% at the first hit (89 vs 89 Mite, 84 vs 88 Uni); "we healthier" only 28-39%.
- **They do not hunt low enemies**: first victim < 50% hp in 8% (Mite) / 12% (Uni) of openers, *below* the 22-23% baseline of low enemies in vision.
  Low enemies are simply out of reach (they recall). When a low victim is available the fight goes 0.94-1.06 kills / 0.4-0.5 deaths.
- **They pick isolated targets**: victim has no ally within 4 in 60% (Mite) / 48% (Uni) of openers vs 35% / 26% baseline. Real fights opened on an
  isolated victim: Mite 0.78/0.35, Uni 0.71/0.46; opened on a grouped, healthy, non-busy victim: Mite 0.68/0.81, Uni 0.59/0.43.
- **Camp-busy enemies**: only a mild preference (victim hitting/being hit by a camp in 13% / 17% of openers vs 11-12% baseline), but these are their best
  fights: Uni 1.20 kills / 0.57 deaths (n=49), Mite 0.83/0.40 (n=30). Examples: Uni collision `e9c3f66b` r284 (Stellar hits Varg farming the altar camp
  at 84% hp; Tavi stun-spell for 506, Issac dashes in, Stellar spells 221+392: Varg and then Issac die, 3-0), Mite collision `bf3fc10f` r46 (Ryth stun on Cassi at a camp, 3-0).
- **Uni opens on recalling enemies** 13% of the time (Mite 2%): a hit interrupts the 5-tick recall.
- **Gems**: they carry gems in 56-64% of openers, so carrying gems does not stop them from fighting.
- **Where**: within 3 tiles of an altar in 41-42% of real fights. Mite opens at 15 tiles from its spawn (42% of its real fights in its own half);
  Uni at 18 (46% in the enemy half). Median round of a real fight: 302 (Mite), 352 (Uni).

**Initiate or stand-and-shoot?** They walk in. Opener movement in rounds r0-3..r0 (m = moved): `mmm.` = 58% (Mite caster), 72% (Uni caster),
58-71% (melee). Only 10% / 8% of caster openers came from a champion that stood still for 4 rounds. The victim also stepped toward the attacker in the
round before the hit in 53-58% of cases, so most openers are two groups closing on each other and the first spell landing at 4-5 tiles.
Over the 4 rounds before the first hit, the attacker closed more distance in 43-45% of cases, the victim in 41-44%.

**Chase**: almost none. After an enemy's first step away from our hitters: median 0 follow steps, 0 tiles moved in the next 12 rounds; >= 3 follow steps in
12% (Mite) / 13% (Uni), and only 6-8% when the victim is below 35% hp. They let it go and the victim dies in 12-14% of cases (20-28% when < 35%).
The rare long chases are melee (Ryth 9-11 steps, interlock `3425ed50` r222 / r229; Varg 10 tiles for a kill, packs `b469f4c8` r252) and almost always cast a spell on the way.

**Avoid**: 241 (Mite) / 223 (Uni) contact episodes (enemy within 5 for 3 rounds, no fight within 5 rounds). Mite avoids mostly with melee (78%) while
*outnumbering* the enemy (60%): a lone Ryth/Varg at 50-90% hp near a Tavi/Stellar does not go in without a spell. Uni avoids when < 50% hp (35%),
outnumbered (35%) or with its spell on cooldown (20% of episodes had a cast within 7 rounds).

Opener by champion: Mite Ryth stun (144: 105 at dist 5, 39 at 4), Stellar (80), Cassi (46), Ren stun (44); Uni Stellar (163), Ren stun (95), Tavi stun (61), Ryth (49), Cassi (35), Prism (37).

## 2. DISENGAGE: when a champion leaves

"First step away" = first round in a fight window where the champion moves and its distance to the nearest enemy grows, dealing no damage in the next 3 rounds.
Restricting to **under fire** (enemy within 4, damage taken in the previous 3 rounds):

| | Mite (n=274) | Uni (n=318) | opponents (n=537) |
|---|---|---|---|
| hp% at the step: median (p25-p75) | 38 (23-57) | 47 (31-69) | 47 (31-64) |
| < 30% / < 50% / >= 70% | 33 / 69 / 15% | 22 / 53 / 25% | 23 / 53 / 19% |
| sustained leave / kite (back in within 8 rounds) | 72 / 17% | 50 / 33% | 68 / 18% |
| outnumbered at the step | 35% | 52% | 37% |
| an ally already dead | 12% | 13% | 11% |
| recall started within 10 rounds | 56% | 28% | 55% |
| died within 12 rounds | 16% | 20% | 17% |

By hp band (leave / died / recalled): Mite 0-30%: 90 / 23 / 74%; 30-50%: 77 / 10 / 65%; 50-70%: 55 / 18 / 34%; 70-100%: 37 / 12 / 17%.
Uni 0-30%: 89 / 32 / 51%; 30-50%: 61 / 16 / 40%; 50-70%: 34 / 23 / 17%; 70-100%: 16 / 11 / 3%.

- **Mite's threshold is hp, Uni's is numbers.** Mite steps out below ~40-50% hp (53% of its under-fire retreats are < 40%) and then recalls (65-74%).
  Uni steps out at ~47% but half of its steps are kites (back within 8 rounds) and 52% happen while outnumbered; a Uni champion at > 70% that steps back
  is kiting 57% of the time, recalling 3%.
- **Melee leave later than casters**: Mite melee 39% / caster 31%; Uni melee 49% / caster 44% (Uni casters with 0 allies around leave earlier).
- **Where they go**: toward own spawn (own-spawn BFS distance drops by > 2 within 12 rounds) 52-57% of sustained leaves, toward the nearest ally 23-29%,
  into a bush within 4 rounds 12-14% (bushes are 1-13% of the map; no measurable bush-seeking: fight-round bush share 5-6% vs 3-7% overall).
- **Recall** is the disengage tool. Recalls started with an enemy within 10: Mite 754 (hp 33% median, distance 7), Uni 521 (hp 29%, distance 8).
  Completion by distance to the nearest enemy, Mite: 3 -> 10%, 5 -> 65%, 6 -> 72%, 7 -> 93%, 8+ -> 94-96%. Uni: <= 4 -> 0-33%, 5 -> 66%, 6-8 -> 67-78%, 9-10 -> 91-95%.
  Mite's rule is clearly "walk until 7 tiles away, then recall" (281+171 of 754 recalls start at exactly 7-8); Uni recalls at 9-10 most often (252 of 521).
- **Does retreating save them?** Under fire: 84% (Mite) / 80% (Uni) survive the next 12 rounds; below 30% hp still 77% / 68%. Of the champions that do die
  in real fights, only 30-31% had started a retreat step: most deaths come from staying (Ren/Issac/Stellar bursts of 200-500 in one round).
  Deaths: 73% of Mite's victims were still >= 50% hp six rounds earlier (Uni 61%); 40% / 47% died with no ally within 4; only 26-32% had >= 2 enemies
  within 3 tiles (burst from range, not a swarm). Killers: Stellar (90 of Mite's 265 deaths, 121 of Uni's 328), Ren, Tavi.
- Examples: saved: Mite collision `30b9ea2d` r179 Ryth at 13% walks from distance 4 to 7, recalls, arrives; Uni corners `373814ef` r55 Ryth at 20% walks out
  of a 4v4 and recalls at distance 6. Died anyway: Mite collision `e9c3f66b` r58 Varg at 34% vs 3 enemies at distance 2; Uni collision `f63abb8a` r248 Tavi at 16% alone vs 3.

## 3. POSITIONING

Distance to the nearest enemy during fight rounds (champion alive, enemy within 8), median (p25-p75) and histogram:

| champion | Mite | Uni | opponents |
|---|---|---|---|
| melee (all) | 4 (2-5); 14% at 1, 17% at 3, 17% at 4 | 4 (3-5); 13% at 1, 20% at 4, 19% at 5 | 4 (2-6) |
| Varg | 4 (2-5), 15% at 1 | 4 (2-5), 18% at 1 | 3 (2-5), 20% at 1 |
| Ryth | 4 (3-5) | 4 (2-5) | 4 (3-5) |
| Ren | 4 (2-5) | 4 (3-5) | 4 (2-5) |
| Issac | 4 (2-6) | 5 (3-6) | 5 (3-6) |
| caster (all) | 5 (4-6); 46% at 4-5 | 4 (3-6); 45% at 4-5 | 5 (3-6) |
| Stellar | 5 (4-6), 28% at exactly 5 | 5 (4-6) | 5 (4-6) |
| Cassi | 5 (4-6) | 4 (4-6) | 5 (4-6) |
| Tavi | 4 (3-6) | 4 (3-6), 23% at 3 | 4 (3-6) |
| Prism | - | 5 (4-6) | 4 (4-6) |
| Willow | - | 4 (3-6), 22% at 3 | 5 (4-7) |

- Casters sit at 4-5: Stellar/Prism at 5 (AoE edge), Cassi at 4 (single-target range 4), Tavi/Willow at 3 (basic-attack range 3 after the stun).
  Melee spend more time at 3-5 than at 1 (Mite melee 14% at distance 1): they are mostly walking into or out of range, not glued to a target.
- Actions in fight rounds: Mite melee move 48% / idle 27% / attack 17% / spell 7%; Mite caster move 47% / idle 29% / spell 14% / attack 10%.
  Uni moves more (caster 56%, melee 59%) and idles less (19% / 16%). The 8-round cooldown dominates: a caster lands a spell in 1 of 7 fight rounds.
- **Kiting** (a ranged champion cannot move in the round it attacks; what does it do the round after an attack/spell?):
  Mite Cassi: attack again 36%, idle 23%, step back 17%, sideways 14%, forward 6%. Mite Stellar: idle 27%, spell 21%, attack 17%, back 14%.
  Uni Tavi: attack again 40%, back 26%, side 17%. Uni Stellar: side 24%, back 22%, spell 16%, forward 15%. Uni Cassi: back 28%, attack 26%, side 23%.
  So Uni's ranged bodies alternate hit / step (back or sideways 40-55%), Mite's stand and hit twice (Cassi 36% double attack, Stellar 27% idle).
- **Front body**: in rounds with both classes present, a melee is strictly closer to the enemy than every caster in 66% of Mite rounds (gap 1.35 tiles) and
  52% of Uni rounds (gap 0.67); opponents 50% (0.37). Mite's Varg/Ryth/Issac wall is real; Uni's Ren/Ryth are only marginally in front of Stellar/Tavi.
- **Formation** (pairwise distances among our champions that have an enemy within 8): Mite mean 3.0, max 4.0, nearest ally 2 (ball with max <= 2: 24%,
  spread max >= 6: 30%, nearest ally adjacent 39%). Uni mean 4, max 5 (ball 19%, spread 41%, adjacent 27%). Mite fights as a tighter clump (Ryth's radius-1 stun and
  Varg's splash want that); Uni spreads (Stellar/Prism AoE on the enemy wants to avoid being clumped itself). Neither forms a line.
- **Terrain**: no use of bushes/holes in fights (bush share 5-6% of fight champion-rounds, equal to the overall share; holes 0%). Walls only matter as vision blockers for the opener.

## 4. GROUPING

Max pairwise distance among the team's eventual participants, N rounds before the first hit (median): Mite 9 (-15) -> 8 (-12) -> 7 (-9) -> 6 (-7..0);
Uni 9 (-15) -> 8 (-11..-7) -> 7 (-6..-4) -> 6 (-3..0). They converge toward the fight but still enter it 6 tiles apart: no "wait at the edge for everyone".

Casters do not hold for the melee: when a caster opens, the nearest melee ally is at median 2 (Mite) / 3 (Uni); within 3 in 68% / 52%; 6+ away in 12% / 30%;
Uni's opening caster has no ally alive nearby at all in 38% of cases (Mite 17%). The caster moved in each of the 3 rounds before the opener in 58% / 72%.
Grouping happens by converging on the same target, not by regrouping first.

## 5. Outcomes per map and opponent (real fights)

| team | map | games (W-L) | real fights | hit first | kills | deaths | dmg dealt/taken per fight |
|---|---|---|---|---|---|---|---|
| Mite | collision | 6 (3-3) | 82 | 54% | 34 | 45 | 779 / 1121 |
| Mite | corners | 6 (3-3) | 86 | 51% | 75 | 96 | 2003 / 2343 |
| Mite | elkring | 6 (5-1) | 66 | 52% | 45 | 44 | 1203 / 999 |
| Mite | interlock | 6 (5-1) | 51 | 35% | 36 | 33 | 1180 / 1335 |
| Mite | lanes | 6 (5-1) | 14 | 50% | 19 | 8 | 1173 / 737 |
| Mite | monolith | 6 (4-2) | 29 | 66% | 12 | 10 | 1063 / 686 |
| Mite | packs | 6 (5-1) | 56 | 73% | 35 | 29 | 1113 / 816 |
| Mite | expanse / rows | 6+6 (2-4, 2-4) | 3 + 2 | - | 5 | 0 | - |
| Uni | collision | 6 (5-1) | 128 | 63% | 93 | 32 | 1790 / 546 |
| Uni | corners | 6 (0-6) | 94 | 50% | 65 | 99 | 2000 / 2266 |
| Uni | elkring | 6 (3-3) | 91 | 58% | 60 | 54 | 1110 / 966 |
| Uni | interlock | 6 (3-3) | 76 | 47% | 40 | 62 | 1029 / 1497 |
| Uni | lanes | 6 (4-2) | 44 | 50% | 37 | 25 | 1192 / 1089 |
| Uni | monolith | 6 (4-2) | 29 | 48% | 20 | 13 | 942 / 752 |
| Uni | packs | 6 (3-3) | 56 | 59% | 25 | 29 | 1088 / 970 |
| Uni | expanse / rows | 6+6 (4-2, 0-6) | 3 + 5 | - | 5 | 6 | - |

Per opponent (kills-deaths, hit first): Mite vs Quantom 35-11 (74%), procless 17-2 (70%), VeryGood 32-35 (56%), Univardisty 38-50 (49%), hello 39-58 (50%),
Intercontinental Fish 39-44, Shawn 42-45, Mate in One 0-8 (25%). Uni vs PTN Hyperion 76-45, hello 70-64 (56%), Mite 50-38 (51%), VeryGood 42-34, geese 25-12 (65%),
Full Damage 18-12 (70%), Shawn 24-49 (69% hit first but lost the trades), Boost 7-22, Mate in One 1-15 (12%). Mate in One beats both in fights by opening first.

Corners is the fight map: 2000+ damage per fight, Mite 75-96, Uni 65-99 (Uni went 0-6 there today). Collision is where Uni dominates (93-32, 77% of damage).
Fights are short: median 5 rounds, 20-22% are single pokes, 5-6% last > 30 rounds (running battles around an altar, e.g. corners `265a46b9` r24-168 Mite vs Uni, Uni 7-0).

## 6. Mite vs Univardisty

| | Mite | Univardisty |
|---|---|---|
| draft bodies | 5-6: Varg, Stellar, Cassi+Issac, Ryth, Ren | 4-5: Ryth, Cassi+Issac, Stellar, Ren / Tavi, Prism, Willow on fight maps |
| opener | Ryth AoE stun at 4-5 (37%), then Stellar/Cassi | Stellar at 5 (31%), Ren/Tavi stun at 4 |
| numbers at own opener | 43% ahead | 54% behind |
| fight location | own half 42% | enemy half 46% |
| formation | tight (max pairwise 4, 39% adjacent), melee in front 66% | spread (max 5, 41% spread), melee in front 52% |
| ranged behaviour after a hit | hit again / idle (Cassi 36% + 23%) | step back or sideways (Tavi 43%, Cassi 51%) |
| retreat trigger | hp < 40-50%, then recall at distance 7 (completion 87%) | outnumbered or hp < 50%; kites at > 70%; recalls at 9-10 (76%) |
| retreat under fire, hp median | 38% | 47% |
| retreat outcome (dies) | 16% | 20% |
| victim profile | isolated 60% | isolated 48%, recalling 13%, camp-busy 17% |
| damage share in fights | 49% | 55% |

Mite plays a melee wall + stun engine: Ryth walks to 4, stuns, Varg/Issac take the front and the casters stand and double-tap; it leaves on an hp rule and
goes home from 7 tiles. Uni plays range: it takes the fight into the enemy half, opens with Stellar at 5 even when outnumbered, keeps its bodies spread so
that AoE answers cost less, kites with Tavi/Cassi, and accepts a lower recall-completion rate because it recalls deeper in enemy territory.

## 7. Rules each team seems to follow

Measured = read directly from the numbers above; inferred = consistent with the numbers but not isolated as a condition.

**Mite**
1. (measured) Open with a spell at 4-5 tiles on the first enemy entering range; walk in to do it (58-71% `mmm.`), do not wait for a numbers edge (43% ahead) or an hp edge.
2. (measured) Prefer an isolated target: 60% of openers on an enemy with no ally within 4 (baseline 35%).
3. (inferred) Melee bodies stay in front of casters (66% of rounds, gap 1.35); casters sit at 5 (Stellar) / 4 (Cassi) and attack twice rather than kite.
4. (measured) Do not chase: 0 follow steps median, >= 3 steps in 12%.
5. (measured) Leave a fight at hp < ~45% (53% of under-fire retreats < 40%, 69% < 50%), walk away toward spawn, start recall when the nearest enemy is >= 7 tiles (93% completion).
6. (measured) A lone melee does not engage casters it outnumbers without a spell ready (60% of avoid episodes while outnumbering).
7. (inferred) Stay compact (nearest ally at 2, adjacent 39%) so the Ryth stun / Varg splash land on clumps.

**Univardisty**
1. (measured) Open with Stellar/Ren/Tavi at 4-5 as soon as an enemy is in range, in the enemy half (46%), even while outnumbered (54%, hit-first rate highest when behind).
2. (measured) Prefer targets that cannot answer: camp-busy (17%, K/D 1.20/0.57), recalling (13%), isolated (48%).
3. (measured) Ranged champions alternate hit and step (back/side 40-55% after an attack); nobody stands still for 2 rounds (idle 10-19%).
4. (measured) Disengage on numbers more than hp: 52% of under-fire retreats while outnumbered; at > 70% hp it is a kite (57%), below 30% a leave (89%) with recall (51%).
5. (measured) Recall late and far: median 9-10 tiles from the nearest enemy; accepts 24% interruptions and a higher death rate after retreating (20%).
6. (measured) Do not chase (13% >= 3 steps), do not regroup before engaging (38% of caster openers with no ally nearby), converge on the target instead.
7. (inferred) Spread formation (max pairwise 5, 41% spread) to limit enemy AoE; melee only marginally in front (52%).

**Shared** (measured): opener is a spell in 87-91% of fights; victim's hp is irrelevant to the decision (8-12% low victims vs 22% available); carrying gems does
not stop a fight (56-64%); bushes/holes are not used; fights last 5 rounds median; 30% of deaths come after an attempted retreat, 70% from staying.
