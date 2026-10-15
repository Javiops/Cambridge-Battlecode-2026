# Targeting and spell use: Mite (#1) vs Univardisty of Shingtonwash (#2)

Data: 108 team-game records (54 Mite, 54 Univardisty, 101 distinct matches, 2026-10-15), per-turn decoded events.
Scripts: `$S/reports/scripts_targeting/` (`load.py` shared loader; `q1_targets.py`, `q1b_rules.py`, `q2_camps.py`, `q3_spells.py`, `q4q5_order_kills.py`, `q6_extra.py`, `q7_examples.py`; raw outputs in `out_*.txt`).
Method notes: "in range" = Chebyshev distance using live positions at the moment of the action (vision not modelled). Spell slots are inferred from effects (damage, dash, heal), from the 8-round cooldown state and, for Stellar/Prism single-vs-area, from the damage multiplier; Varg/Ryth attack-reset is recognised as a cast sandwiched between two basic attacks, otherwise shield / empty stun. Residual misclassification about 1-2%.

## 1. Target choice on enemy champions

Decisions with 2+ enemies in range of the attack (basic: 1 melee / 3 ranged; single-target spells: 4): Mite 478 (mean 2.15 candidates), Univardisty 611 (2.27). Random baseline 0.46-0.48.

| hypothesis (target is the ...) | Mite hit | Mite, only when it singles out a subset | Uni hit | Uni, subset only |
|---|---|---|---|---|
| lowest absolute hp | 0.69 | 0.69 (n=478) | 0.71 | 0.71 (n=608) |
| lowest hp% | 0.72 | 0.72 (n=473) | 0.67 | 0.66 (n=594) |
| nearest | 0.92 | **0.77** (n=172) | 0.78 | 0.51 (n=278) |
| most gems carried | 0.79 | 0.44 (n=183) | 0.87 | 0.59 (n=200) |
| a ranged champion (casters first) | 0.77 | 0.44 (n=197) | 0.85 | 0.67 (n=286) |
| already damaged by an ally this round | 0.88 | 0.64 (n=161) | 0.93 | 0.70 (n=150) |
| hit by the team in the last 3 rounds | 0.90 | 0.80 (n=250) | 0.85 | 0.71 (n=312) |
| same target as my previous hit (sticky, <=3 rounds) | 0.88 | 0.81 (n=311) | 0.88 | 0.78 (n=320) |
| killable by this hit | 0.99 | 0.89 (n=27) | 0.99 | 0.88 (n=32) |

Head-to-head when two hypotheses name different targets:

| conflict | Mite | Univardisty |
|---|---|---|
| lowest hp vs nearest | nearest 0.59 (n=91) | **lowest hp 0.56** (n=137) |
| lowest hp vs lowest hp% | hp% 0.61 (n=59) | hp 0.62 (n=92) |
| lowest hp vs ranged-first | lowest hp 0.80 (n=64) | lowest hp 0.65 (n=71) |
| lowest hp vs most gems | lowest hp 0.74 (n=80) | lowest hp 0.50 / gems 0.39 (n=101) |
| lowest hp vs sticky | sticky 0.61 (n=82) | sticky 0.54 (n=104) |
| nearest vs sticky | sticky 0.60 (n=15) | sticky 0.85 (n=47) |
| nearest vs ranged-first | nearest 0.75 (n=53) | ranged 0.56 (n=75) |

Best lexicographic rules found by search (`q1b_rules.py`, ties split evenly):

| team | all decisions | melee | ranged basic attacks | single-target spells |
|---|---|---|---|---|
| Mite | killable > nearest > lowest hp%: **0.76** | killable > sticky > nearest > lowest hp: 0.78 | killable > lowest hp% > sticky: 0.88 | killable > nearest > sticky: 0.71 |
| Univardisty | killable > sticky > lowest hp: **0.73** | killable > sticky > lowest hp > nearest: 0.71 | killable > ally-damaged > most gems > lowest hp: 0.82 | killable > sticky > lowest hp: 0.69 |

Neither team targets casters first or gem carriers as such (gem carriers are hit mostly because they are also the low-hp ones). Both finish killable targets (0.88-0.89) and both are sticky. Mite's ranged units prefer the closest enemy in range (Stellar casts at 3 on the nearest, e.g. 265a46b9 r76 Stellar1 single on Tavi 715hp at d3 instead of Ren 520hp at d4); Univardisty's units go for the lowest-hp one even at range 4 (37e16f73 r90 Ren6 stun on Issac 415hp at d4 instead of Ren 1085hp at d2; 1c547a16 r278 Stellar4 single on Cassi 326hp at d4 instead of Stellar 603hp at d3).

Focus: in rounds where the team damages champions, a single victim receives all damage in 92% of rounds (both teams). In rounds where 2+ team champions hit champions, all hit the same victim 66% (Mite, n=689) / 63% (Uni, n=661); when split, the main victim still gets 65% / 70% of the damage. Split damage comes mostly from area spells and melee that cannot reach the focus target.

Switching: consecutive hits by the same champion (<=3 rounds apart) change target 11% (Mite) / 14% (Uni). Reasons: previous target out of range 51% / 53%, previous target dead 23% / 19%, new target has lower hp 12% / 15%, other 12% / 12%. Example of a deliberate switch: a19f0480 r27 Mite Cassi2 11->6 (lower hp); e9c3f66b r52 Uni Tavi0 4->6 (previous left range).

## 2. Target choice on camps

| | Mite | Univardisty |
|---|---|---|
| engagements (first hit on a group after 12+ idle rounds) | 1845 | 1686 |
| monster awake at first hit | 8% | 13% |
| elk + gold_cluster group: elk hit first | 150 vs 25 | 134 vs 38 |
| gem,gem,gold,gold group: gold_cluster first | 38 vs 16 | 27 vs 1 |
| elk + 3 gem_cluster: elk first | 2 vs 9 | 22 vs 14 |
| groups with unequal hp: highest-hp monster first | 59% | 65% |
| same monster when 2+ champions hit the group in a round | **0.90** (n=6002) | 0.84 (n=4376) |
| champions hitting an engagement: 1 / 2 / 3 / 4 | 229 / 139 / 42 / 11 | 314 / 96 / 27 / 3 |
| first hitter is the one the monster attacks | 84% (n=296) | 89% (n=267) |
| monster hits taken by melee | 78% | 62% |
| mixed melee+ranged engagements: melee takes the aggro | 76% (n=78) | 81% (n=48) |

Both teams open on the big monster of a group (elk 2400 hp, which also carries the aggro) and hit it with everyone until it dies, then the clusters. Ranged champions attack monsters from exactly 3 tiles: Cassi 86% (Mite) / 97% (Uni) of camp basics at d3, Stellar 89% / 92%, Tavi 82% / 91%; the rest at 1-2 are mostly after walking in. Varg attacks at d1 (Mite 92%) but Uni's Varg attacks at d2 28% (splash on the neighbour). Tank distribution (monster hits taken): Mite Issac 4680, Ren 3301, Ryth 2569, Varg 1636, Cassi 1428, Stellar 1048, Tavi 119; Uni Issac 3113, Ren 2306, Varg 1778, Stellar 1493, Cassi 1315, Ryth 1208, Tavi 916. Univardisty farms solo far more (71% solo engagements), so its ranged champions tank their own camps more often. Mite's Cassi stuns the awake elk so it skips its attack (see 3.3).

## 3. Spells

### 3.1 Casts per game, target class, distance, timing

Mite (54 games):

| champion / slot | casts/game | on champ | on camp | recast exactly at cooldown end | distance mode (share) | 2+ champions hit |
|---|---|---|---|---|---|---|
| Cassi dmg (2F, excl.) | 24.3 | 19% | 81% | 41% | 3 (73%), 4 (14%) | - |
| Cassi stun | 8.6 | 55% champ / 44% elk | - | 29% | - | - |
| Issac reset | 21.5 | 11% double-hit on champ | 88% on camp | 39% | - | - |
| Issac dash | 31.4 | - | - | 40% | - | - |
| Ryth area stun (1F) | 19.0 | 49% | 51% | 47% | 1 (50%), 5 (23%) | 103/505 on champs |
| Ryth reset | 13.1 | 15% | 84% | 36% | - | - |
| Stellar single (2F) | 14.3 | 27% | 73% | 34% | 3 (72%), 4 (15%) | - |
| Stellar area (1.4F) | 16.0 | 35% | 65% | 41% | 3 (57%), 5 (21%) | 69/301 on champs |
| Tavi stun (2.2F) | 2.4 | 12% | 88% | 50% | 3 (74%) | - |
| Tavi reset | 1.9 | 5% | 91% | 38% | - | - |
| Ren stun (1.25F) | 19.9 | 29% | 71% | 38% | 1 (73%), 4 (16%) | - |
| Ren dash | 27.8 | - | - | 40% | - | - |
| Varg reset | 14.5 | 18% | 82% | 37% | - | - |
| Varg shield | 15.1 | cast while attacking a camp 74%, enemy in 4 only 28% | | 36% | - | - |

Univardisty (54 games):

| champion / slot | casts/game | on champ | on camp | recast at cooldown end | distance mode (share) | 2+ champions hit |
|---|---|---|---|---|---|---|
| Cassi dmg | 13.8 | 21% | 79% | 49% | **4 (55%)**, 3 (41%) | - |
| Cassi stun | 9.8 | 31% champ / 69% camp | - | 22% | - | - |
| Issac reset | 11.2 | 6% | 92% | 44% | - | - |
| Issac dash | 12.6 | - | - | 33% | - | - |
| Ryth area stun | 12.6 | 51% | 49% | 54% | **5 (39%)**, 1 (25%) | 100/349 |
| Ryth reset | 6.6 | 31% | 67% | 30% | - | - |
| Prism single (1.5F) | 6.3 | 22% | 78% | 37% | 4 (49%), 3 (39%) | - |
| Prism area (1F) | 7.4 | 25% | 75% | 51% | 3 (41%), 5 (36%) | 24/100 |
| Stellar single | 19.6 | 30% | 70% | 35% | **4 (61%)**, 3 (28%) | - |
| Stellar area | 23.6 | 38% | 62% | 44% | **5 (49%)**, 3 (29%) | 101/480 |
| Tavi stun | 16.6 | 35% | 65% | 44% | **4 (54%)**, 3 (37%) | - |
| Tavi reset | 11.9 | walk-reset-shoot 48% | 39% camp double-hit | 32% | - | - |
| Ren stun | 21.4 | 45% | 55% | 47% | **4 (47%)**, 1 (26%) | - |
| Ren dash | 17.3 | - | - | 37% | - | - |
| Varg reset | 7.2 | 12% | 88% | 40% | - | - |
| Varg shield | 10.6 | enemy in 4 25%, own hp<50% 32% | | 65% | - | - |
| Marcella dmg | 2.9 | 37% | 63% | 38% | 4 (49%), 1 (33%) | - |
| Willow heal (3F) | 1.6 | target <50% hp 80%, <70% 100%; enemy near target 44% | | 33% | - | - |
| Vendetta reset | 2.7 | 1% | 99% | 33% | - | - |

"Distance" for Ryth/Stellar/Prism area = caster to the farthest victim; 5 means the ground target was placed at 4 and the radius-1 splash reached 5. Univardisty consistently casts at the edge of range (4, or 5 via the AoE radius); Mite casts from 3, i.e. from basic-attack range, and only 14-23% of its casts come from 4-5.

### 3.2 Usage rate when the slot is available (turn-level opportunities)

| champion / slot | Mite: enemy champ within 4 | Mite: camp only within 4 | Uni: enemy champ within 4 | Uni: camp only |
|---|---|---|---|---|
| Cassi dmg | 0.88 (n=299) | 0.30 | 0.57 (n=278) | 0.34 |
| Cassi stun | 0.56 (n=398) | 0.03 | 0.36 (n=211) | 0.11 |
| Ryth area stun | 0.82 (n=351) | 0.21 | 0.68 (n=329) | 0.26 |
| Stellar single / area | 0.76 / 0.63 | 0.28 / 0.34 | 0.63 / 0.55 | 0.19 / 0.21 |
| Prism single / area | - | - | 0.58 / 0.54 | 0.22 / 0.25 |
| Tavi stun | 1.00 (n=16) | 0.43 | 0.86 (n=370) | 0.20 |
| Ren stun | 0.85 (n=366) | 0.26 | 0.88 (n=597) | 0.16 |
| Marcella dmg | - | - | 0.49 | 0.22 |
| Varg shield | 0.21 (n=990) | 0.16 | 0.41 (n=311) | 0.10 |

| attack resets, used when ... | Mite: attacked a champion | Mite: attacked a camp | Uni: champion | Uni: camp |
|---|---|---|---|---|
| Issac | 0.50 (n=251) | 0.92 | 0.96 (n=47) | 0.96 |
| Ryth | 0.76 | 0.87 | 0.69 | 0.89 |
| Varg | 0.89 | 0.96 | 0.55 | 0.86 |
| Tavi | 0.90 (n=10) | 0.64 | 0.77 (n=252) | 0.82 |
| Marcella / Willow / Vendetta / Vesper | - | - | 1.00 / 0.94 / 1.00 / 1.00 | 0.97 / 0.97 / 0.91 / 0.92 |

The missing casts against champions are almost all turns where the champion walked (exclusive spells) or cast the other slot (one cast per turn): nobody saves a spell. Stun spells are not held for kills or for chasers:

| context of the stun cast on a champion | Mite Ren (n=311) | Uni Ren (n=524) | Uni Tavi (n=316) | Mite Cassi dmg (n=255) |
|---|---|---|---|---|
| target killed by the cast | 0.07 | 0.06 | 0.13 | 0.09 |
| target dead within 2 rounds | 0.17 | 0.12 | 0.20 | 0.17 |
| target hp < 35% | 0.15 | 0.13 | 0.08 | 0.14 |
| target was moving away from the caster | 0.39 | 0.34 | 0.35 | 0.29 |
| target had a recall in progress | 4 | 6 | 7 | 0 |
| caster hp < 40% | 0.21 | 0.19 | 0.19 | 0.11 |

Univardisty's hits on recalling enemies: 304 (165 by spell, 139 by basic) vs Mite 30; that is a consequence of Uni's longer reach and more fighting, not a stun rule (recall is interrupted by any damage). Ryth's area stun lands on a recalling enemy 43 times for Uni (e.g. 265a46b9 r683 Ryth4 on recalling Ryth6) vs 4 for Mite.

Stellar / Prism single vs area when both slots are up and an enemy is within 4: Mite Stellar chose single 45, area 13, no cast 28 (n=86); with a 2-enemy cluster available (9 cases): area 7, single 2. Uni Stellar: single 55, area 29, no cast 46 (n=130); cluster available (21): area 11, single 1. Prism (Uni): single 13, area 8. So: single by default, area when 2+ enemies sit within radius 1 of one tile; otherwise the slots simply alternate on cooldown (other slot on cooldown at 54-85% of casts, consecutive rounds single/area/single). Area casts hit 2+ champions 21-23% of the time (Stellar), 20-29% (Ryth); examples: bf3fc10f r54 Mite Ryth5 stuns 4 (Ren, Stellar, Cassi, Issac); 265a46b9 r321 Uni Prism8 area hits 4; 1c547a16 r275 Uni Stellar4 area hits 3 for 224 each.

Cassi stun (no visible target; inferred from who skips the next turn): Mite 463 casts: 257 with an enemy within 4 (an enemy then skips its next turn in 83% of these), 204 with only a camp in range, 198 of them on an elk: in all 119 cases where the elk had attacked the previous round it does not attack the next one, i.e. Mite stuns the elk on cooldown to cancel its 2-round attack (a8ac14b5 r321 Cassi2; a3d60396 r130 Cassi7). Uni's 278 camp stuns are mostly on wolves/gem clusters and only halve the monster's next attack (51/102 still attack) - mostly wasted. Cassi does not use the stun to escape (she moves away afterwards in 9% Mite / 0% Uni) nor to interrupt channels (8 recalling targets for Uni, 0 for Mite).

Dashes (Issac, Ren, Vendetta, Vesper): a travel tool. 94% (Mite) / 99.7% (Uni) of dashes are in a turn that also walks, 81% / 73% with no enemy within 8. With an enemy within 6: Mite Issac dashes toward 8% / away 7% and attacks after the dash in 7% of all dashes (Issac 112 and Ren 102 "dash then attack" turns on champions, e.g. 'cast:dash atk'); Uni dashes away 10-16% and toward 3-8%, never attacks after a dash (e.g. 502126ec r134 Issac3 dashes away at 25/900 hp; 3e165d6b r86 VesperVale6 at 20/900). Only 4-6% of dashes happen below 40% hp (Mite) vs 7-15% (Uni).

Attack resets are a farming tool for both: 82-99% of resets double-hit a monster; on champions 5-18% (Ryth Uni 31%). Vendetta's reset follows a kill in the same turn only 4% of the time (its kills are camp kills; resets 99% on camps). Uni's Tavi/Willow/Vesper use the reset to walk and still shoot (48% / 67% / 53% of their resets are walk-reset-shoot: e9c3f66b r48 Tavi0); Mite's Tavi does this 4%.

Varg shield: Mite casts it as a farming buffer (74% while attacking a camp; 79% usage vs an awake monster, 2% vs a sleeping one), Uni as a fight/escape buffer (own hp<50% 32%, enemy within 4 25%, recast at cooldown end 65%).

### 3.3 Spells on camps

Casts on camps per game: Mite Cassi dmg 19.6, Ren stun 14.1, Stellar area 11.0, Ryth area stun 10.7, Stellar single 10.5, Tavi 2.1; Uni Stellar area 15.6, single 13.8, Ren 11.7, Cassi 10.9, Tavi 10.7, Ryth 6.7, Prism 5.7 + 4.9, Marcella 1.8. Usage when the champion is basic-attacking a camp, no enemy within 6 and the slot is up:

| champion / slot | Mite (awake / asleep monster) | Uni (awake / asleep) |
|---|---|---|
| Cassi dmg | 1.00 / 1.00 (n=837) | 0.98 / 1.00 (n=326) |
| Tavi stun | 1.00 (n=75) | 0.93 / 1.00 (n=310) |
| Ren stun | 0.71 / 0.12 (n=1258) | 0.96 / 0.33 (n=321) |
| Ryth area stun | 0.72 / 0.20 (n=819) | 0.93 / 0.21 (n=175) |
| Stellar single / area | 0.75 / 0.51 ; 0.83 / 0.56 | 0.91 / 0.64 ; 0.92 / 0.39 |
| Prism single / area | - | 0.85 / 0.82 ; 0.87 / 0.19 |
| Cassi stun | 0.05 overall, **0.48 on elk**, 0 otherwise | 0.02 |
| Varg shield | 0.79 / 0.02 | 0.14 / 0.06 |

Both teams burn damage spells on monsters on cooldown; stuns (Ren, Ryth) are held off sleeping monsters, so melee stun spells are used as "the monster is awake, shorten the fight" tools. Spell share of camp damage: Stellar 77% (Mite) / 81% (Uni), Cassi 57% / 55%, Tavi 59% / 67%, Ren 31% / 52%, Ryth 28% / 31%, Prism 69%.

### 3.4 Spell share of champion damage

| | Mite | Univardisty |
|---|---|---|
| damage to enemy champions per game | 10,193 | 15,508 |
| spell share | **62%** | **76%** |
| Stellar / Cassi / Tavi spell share | 93% / 83% / 81% | 95% / 84% / 87% |
| Ren / Ryth spell share | 68% / 68% | 80% / 53% |
| Stellar champion damage per game (atk+spell) | 2,808 | 5,133 |
| Tavi | 117 (6 games) | 3,100 |
| Ren | 1,624 | 2,608 |
| Issac / Varg (basics only) | 1,031 / 1,205 | 386 / 788 |

Univardisty's champion damage is a caster line (Stellar + Tavi + Ren = 70%); Mite's is spread across the 6-champion draft, its melee contributing 38%.

## 4. Attack + move order within a turn

Measured from the event order in turns that hit something (`q4q5_order_kills.py`):

| | Mite | Univardisty |
|---|---|---|
| exclusive spells (Cassi dmg, Stellar, Prism, Tavi stun, Ren stun, Ryth stun, Marcella dmg) cast in a turn with a walk | 0 of 5,196 | 0 of 6,120 |
| melee vs champions: walk then hit / hit then walk | Issac 224 / 152, Ren 148 / 124, Ryth 175 / 133, Varg 251 / 165 | Issac 86 / 79, Ren 273 / 256, Ryth 216 / 201, Varg 128 / 105 |
| melee vs camps: walk then hit / hit then walk | 718 / 315 (Issac) | 376 / 200 (Issac) |
| melee reset pattern | `mv atk reset atk` (Issac 530, Ryth 332, Varg 353 on camps) | same (Issac 310, Ryth 160, Varg 203) |
| ranged basic attack in a turn with a walk | only via reset: Tavi 4 | Tavi 307 (`mv reset atk`), Willow 74, Vesper 33 |
| caster order with basic | `cast then atk` (Cassi 889+95, Stellar 874+218) | `atk then cast` (Cassi 292, Stellar 746) - same effect |
| dash then attack (champion) | Issac 112, Ren 102 | 0 (atk then dash 12) |
| free casts (resets, dash, Cassi stun, shield) after a walk | common (`free_mv_then_cast` Varg 119 champ / 381 camp) | common (Tavi 123 / 184) |

Rules: melee walk-then-hit when approaching (60%), hit-then-walk when the target is already adjacent and they want to reposition (40%); ranged never trade the shot for a step except through the attack reset (Univardisty does this systematically with Tavi/Willow/Vesper, Mite almost never); exclusive casters position one round and cast the next without moving (engine rule, never violated); Mite's melee dash into melee range and hit in the same turn, Univardisty's melee use the dash only to leave.

## 5. Kill securing and last hits

| | Mite | Univardisty |
|---|---|---|
| kills (247 / 332) per game | 4.6 | 6.1 |
| by champion type | Stellar 58, Ren 47, Ryth 41, Issac 33, Cassi 33, Varg 30, Tavi 5 | Stellar 83, Ren 72, Tavi 60, Ryth 43, Varg 26, Issac 18, Cassi 13, Prism 12, Marcella 5 |
| killing blow by spell | 50% | 62% |
| killer is the top damage dealer on the victim (last 4 rounds) | 69% | 80% |
| victim carried gems | 31% (mean 19 gems per kill) | 31% (18) |
| ally in range of the victim who acted before the killer in the kill round | 36: hit the victim 31, hit someone else 2, did not attack 3 | 18: hit the victim 15, did not attack 3 |
| share of a game's kills by its top killer type | 0.58 | 0.60 |

There is no last-hit arrangement: an ally in range of a dying enemy almost always hits it (31/36, 15/18); the three Mite "did not attack" cases are Cassi out of a basic-attack but in spell range (d6b437f2 r29 Cassi7 vs Ren3 at 20 hp, Varg5 finished). Kills go to whoever has the biggest hit available, which is the caster line (Stellar/Ren/Tavi take 59% of Mite's and 65% of Uni's kills).

## 6. Mite vs Univardisty

| | Mite | Univardisty |
|---|---|---|
| target choice with 2+ in range | killable > **nearest** > lowest hp% (0.76) | killable > **keep current target** > lowest absolute hp (0.73) |
| ranged basic attacks | lowest hp% (0.88) | ally-damaged / gem carrier / lowest hp (0.82) |
| cast distance | 3 (basic-attack range), 14-23% at 4-5 | 4, area at 5 (55-61% of single-target casts at 4) |
| spell use vs champions | cast on sight, 0.76-0.88 of available turns | 0.55-0.88, misses are walking turns |
| spell share of champion damage | 62% (10.2k/game) | 76% (15.5k/game) |
| Cassi stun | elk-denial (198 on elk, 100% attack cancelled) + champions | mostly on wolves, half wasted |
| dash | travel + engage (dash-then-hit 214 turns) | travel + escape (away 10-16%, never dash-then-hit) |
| attack reset on ranged | not used for kiting | walk-reset-shoot 48-67% of Tavi/Willow/Vesper resets |
| Varg shield | farming buffer vs awake monsters | fight buffer below 50% hp |
| camp first target | elk first (6:1), all on the same monster 90% | elk first (3.5:1), same monster 84%, 71% solo farming |
| focus (2+ attackers same victim) | 66% | 63% |
| kills/game, spell kills | 4.6, 50% | 6.1, 62% |

## 7. Rule list per team

Measured (M) with threshold; inferred (I) where the behaviour is consistent but the exact condition is not observable.

Mite
1. (M) Target: if any enemy in range dies to this hit, hit it (89%); else the nearest enemy in range (77% when nearest is unique); tie-break lowest hp% (72%); keep the current target while it stays in range (81%).
2. (M) Ranged basics pick the lowest hp% enemy within 3 (88%); melee stay on the adjacent target they hit last round (78%).
3. (M) No caster-first or gem-carrier rule (0.44 when informative).
4. (M) Casters attack and cast from 3 (Cassi 73%, Stellar 72%, Tavi 74%); exclusive spells cast only on turns without a walk (100%, engine).
5. (M) Damage/stun spells cast whenever an enemy champion is within 4 and the slot is up (Cassi 0.88, Ren 0.85, Ryth 0.82, Stellar 0.63-0.76); no saving for kills (7-9% of casts kill).
6. (M) Stellar: single-target by default; area when 2+ enemies are within radius 1 of one tile (7 of 9); slots alternate on consecutive rounds.
7. (M) Cassi stun: on an enemy within 4 if present, else on an awake elk being farmed (48% of elk farm turns, 0% on other monsters).
8. (M) Camp spells: Cassi/Tavi on cooldown on any monster (1.00); Ren/Ryth stun and Varg shield only on an awake monster (0.71-0.79 vs 0.02-0.20 asleep); Stellar both slots 0.68-0.76.
9. (M) Attack resets: after a basic on a camp 0.87-0.96; on champions Issac only 0.50 (I: Issac reset kept for farm turns), Varg 0.89.
10. (M) Dash: travel with the walk (94%), and dash-then-attack to close on a champion (Issac 112, Ren 102 turns).
11. (M) Camps: open on the elk (150:25), everyone on the same monster (90%), ranged at exactly 3, melee tank (76% in mixed groups).
12. (M) Melee: walk then hit when approaching (60%), hit then walk otherwise; no last-hit arrangement.

Univardisty
1. (M) Target: killable first (88%); else keep the current target (85% vs nearest, 54% vs lowest hp); else lowest absolute hp in range (0.71; beats nearest 0.56, beats hp% 0.62, beats ranged-first 0.65).
2. (M) Ranged basics: the enemy an ally already damaged this round / gem carrier / lowest hp (0.82).
3. (M) Casts at max range: Cassi 55% at 4, Stellar single 61% at 4, Tavi 54% at 4, Ren stun 47% at 4, area spells placed so the splash reaches 5 (Stellar 49%, Ryth 39%).
4. (M) Damage/stun spells vs champions whenever possible: Ren 0.88, Tavi 0.86, Ryth 0.68, Stellar 0.55-0.63, Cassi 0.57 (the rest are walking turns); 6-13% of stun casts kill, 34-35% land on a target moving away (chase, not a saved spell).
5. (M) Stellar/Prism: single by default, area when a 2-cluster exists (11 of 12 casts); slots alternate.
6. (M) Camp spells on cooldown on awake monsters (0.85-0.98), rarely on sleeping ones except Cassi/Tavi/Prism single (0.64-1.00); Varg shield is a fight tool (hp<50% 32%).
7. (M) Attack reset: ranged walk-reset-shoot (Tavi 48%, Willow 67%, Vesper 53%); melee double-hit on camps (0.86-0.96).
8. (M) Dash = travel (99.7% with a walk) or retreat (away 10-16% when an enemy is within 6, never dash-then-hit).
9. (M) Willow heal when an ally is below 70% hp (100%), mostly below 50% (80%).
10. (M) Camps: elk first (134:38), gold cluster before gem clusters (27:1), solo farming 71%, same monster 84%, ranged at 3 (91-97%), first hitter tanks (89%).
11. (M) Cassi stun on champions 31% of casts, otherwise on the monster being farmed (low value: monster still attacks 50%).
12. (M) No last-hit arrangement; kills go to the caster line (Stellar/Ren/Tavi 65%).
