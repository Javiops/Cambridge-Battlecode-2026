## Q1. Reaction to being hit

Unit = champion-round in which the champion took damage from an enemy champion ("hit round"). Action classes: **fight** = basic attack or damage spell on an enemy champion (fight+away / fight+closer = a melee that also moved); **away / closer / lateral** = moved and the Chebyshev distance to the nearest enemy (enemy positions of the previous round end) grew / shrank / stayed; **camp** = attacked a camp monster; **recall / tribute** = started or continued that channel; **nothing** = no action with an effect (idle, failed action, stunned); **dead**.

Counts: hit rounds us 7606 (2866 episodes), opponents 8094 (3450 episodes). Episode = hit rounds of one champion with gaps <= 5 rounds.

### US: action in the hit round (t0) and the next 3 rounds (all hit rounds)

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| t+0 | 7606 | 22% | 6% | 4% | 15% | 13% | 5% | 2% | 0% | 3% | 20% | 9% |
| t+1 | 7606 | 21% | 7% | 3% | 23% | 4% | 5% | 1% | 2% | 2% | 19% | 15% |
| t+2 | 7606 | 17% | 5% | 2% | 27% | 6% | 5% | 1% | 5% | 1% | 11% | 20% |
| t+3 | 7606 | 12% | 4% | 2% | 27% | 7% | 4% | 1% | 9% | 1% | 9% | 24% |

### US: by champion type, action in the hit round / at t+1 (first hit of each episode only)

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cassi t0 | 327 | 21% | 0% | 0% | 12% | 28% | 5% | 3% | 0% | 3% | 22% | 6% |
| Cassi t+1 | 327 | 13% | 0% | 0% | 26% | 3% | 4% | 1% | 0% | 2% | 42% | 8% |
| Issac t0 | 352 | 7% | 5% | 10% | 12% | 30% | 3% | 3% | 0% | 5% | 21% | 4% |
| Issac t+1 | 352 | 10% | 6% | 7% | 22% | 7% | 2% | 1% | 1% | 4% | 32% | 7% |
| Prism t0 | 197 | 31% | 0% | 0% | 7% | 16% | 6% | 1% | 1% | 3% | 32% | 3% |
| Prism t+1 | 197 | 37% | 0% | 0% | 15% | 3% | 5% | 0% | 2% | 2% | 30% | 6% |
| Ren t0 | 674 | 15% | 3% | 6% | 11% | 23% | 3% | 4% | 0% | 4% | 29% | 2% |
| Ren t+1 | 674 | 21% | 6% | 3% | 22% | 8% | 4% | 2% | 2% | 3% | 24% | 4% |
| Ryth t0 | 308 | 9% | 1% | 8% | 13% | 35% | 9% | 2% | 0% | 5% | 17% | 1% |
| Ryth t+1 | 308 | 19% | 3% | 3% | 14% | 4% | 6% | 2% | 1% | 5% | 40% | 3% |
| Stellar t0 | 531 | 34% | 0% | 0% | 13% | 14% | 2% | 1% | 0% | 3% | 30% | 3% |
| Stellar t+1 | 531 | 33% | 0% | 0% | 17% | 5% | 3% | 1% | 2% | 2% | 31% | 7% |
| Tavi t0 | 310 | 17% | 0% | 0% | 17% | 10% | 3% | 2% | 0% | 4% | 43% | 4% |
| Tavi t+1 | 310 | 22% | 0% | 0% | 27% | 7% | 7% | 3% | 5% | 3% | 20% | 8% |
| Varg t0 | 73 | 5% | 4% | 8% | 16% | 36% | 1% | 4% | 1% | 7% | 14% | 3% |
| Varg t+1 | 73 | 10% | 5% | 7% | 18% | 11% | 4% | 1% | 0% | 7% | 34% | 3% |
| Vendetta t0 | 94 | 3% | 3% | 10% | 6% | 51% | 6% | 4% | 0% | 1% | 15% | 0% |
| Vendetta t+1 | 94 | 5% | 9% | 5% | 24% | 4% | 4% | 2% | 0% | 2% | 39% | 4% |

### US: by hp band before the hit (all hit rounds), action at t0 / t+1

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hp >70 t0 | 3426 | 24% | 4% | 5% | 11% | 20% | 4% | 2% | 0% | 4% | 25% | 1% |
| hp >70 t+1 | 3426 | 25% | 5% | 4% | 19% | 7% | 5% | 2% | 1% | 3% | 29% | 3% |
| hp 40-70 t0 | 2430 | 27% | 8% | 5% | 16% | 10% | 6% | 1% | 0% | 2% | 21% | 3% |
| hp 40-70 t+1 | 2430 | 23% | 9% | 3% | 28% | 4% | 5% | 1% | 3% | 1% | 15% | 8% |
| hp <40 t0 | 1750 | 13% | 10% | 1% | 23% | 3% | 5% | 0% | 1% | 1% | 11% | 32% |
| hp <40 t+1 | 1750 | 8% | 7% | 0% | 26% | 1% | 3% | 0% | 2% | 0% | 3% | 48% |

### US: by champion class x hp band, action at t+1 (all hit rounds)

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| melee hp >70 | 1943 | 21% | 8% | 7% | 17% | 8% | 4% | 2% | 1% | 3% | 28% | 2% |
| melee hp 40-70 | 1454 | 20% | 15% | 5% | 26% | 5% | 4% | 1% | 2% | 2% | 16% | 5% |
| melee hp <40 | 818 | 9% | 15% | 1% | 26% | 1% | 2% | 0% | 2% | 0% | 4% | 40% |
| caster hp >70 | 1483 | 32% | 0% | 0% | 21% | 5% | 5% | 1% | 1% | 2% | 29% | 3% |
| caster hp 40-70 | 976 | 28% | 0% | 0% | 31% | 3% | 7% | 0% | 3% | 1% | 15% | 12% |
| caster hp <40 | 932 | 8% | 0% | 0% | 27% | 1% | 4% | 0% | 2% | 0% | 2% | 55% |

### OPPONENTS: action in the hit round (t0) and the next 3 rounds (all hit rounds)

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| t+0 | 8094 | 19% | 5% | 8% | 13% | 20% | 4% | 1% | 1% | 4% | 22% | 5% |
| t+1 | 8094 | 18% | 5% | 5% | 24% | 10% | 4% | 1% | 1% | 3% | 19% | 9% |
| t+2 | 8094 | 15% | 4% | 5% | 31% | 14% | 5% | 1% | 3% | 2% | 9% | 11% |
| t+3 | 8094 | 12% | 3% | 4% | 32% | 14% | 5% | 2% | 6% | 2% | 7% | 13% |

### OPPONENTS: by champion type, action in the hit round / at t+1 (first hit of each episode only)

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cassi t0 | 381 | 20% | 0% | 0% | 10% | 29% | 4% | 3% | 0% | 5% | 23% | 5% |
| Cassi t+1 | 381 | 15% | 0% | 0% | 25% | 9% | 4% | 3% | 0% | 3% | 31% | 8% |
| Issac t0 | 604 | 7% | 3% | 9% | 9% | 38% | 4% | 1% | 0% | 4% | 21% | 3% |
| Issac t+1 | 604 | 8% | 4% | 6% | 24% | 14% | 5% | 1% | 1% | 4% | 27% | 5% |
| Marcella t0 | 28 | 36% | 4% | 0% | 21% | 25% | 0% | 0% | 0% | 7% | 0% | 7% |
| Marcella t+1 | 28 | 21% | 0% | 4% | 29% | 21% | 4% | 0% | 0% | 4% | 0% | 18% |
| Prism t0 | 112 | 20% | 0% | 0% | 8% | 24% | 4% | 5% | 1% | 4% | 32% | 3% |
| Prism t+1 | 112 | 25% | 0% | 0% | 19% | 12% | 6% | 4% | 0% | 2% | 25% | 7% |
| Ren t0 | 516 | 11% | 1% | 8% | 12% | 31% | 4% | 2% | 0% | 7% | 22% | 2% |
| Ren t+1 | 516 | 15% | 1% | 4% | 18% | 14% | 4% | 2% | 1% | 6% | 29% | 5% |
| Ryth t0 | 335 | 6% | 3% | 7% | 8% | 38% | 5% | 0% | 1% | 6% | 25% | 1% |
| Ryth t+1 | 335 | 15% | 3% | 4% | 19% | 18% | 5% | 1% | 0% | 4% | 28% | 3% |
| Stellar t0 | 574 | 27% | 0% | 0% | 6% | 25% | 3% | 1% | 0% | 7% | 27% | 4% |
| Stellar t+1 | 574 | 23% | 0% | 0% | 17% | 12% | 5% | 2% | 1% | 5% | 28% | 6% |
| Tavi t0 | 317 | 16% | 0% | 3% | 8% | 25% | 3% | 2% | 0% | 5% | 37% | 2% |
| Tavi t+1 | 317 | 24% | 0% | 1% | 21% | 11% | 7% | 3% | 0% | 5% | 23% | 5% |
| Varg t0 | 307 | 8% | 4% | 11% | 9% | 35% | 3% | 1% | 0% | 8% | 20% | 2% |
| Varg t+1 | 307 | 7% | 3% | 7% | 17% | 15% | 4% | 1% | 0% | 7% | 35% | 3% |
| Vendetta t0 | 198 | 6% | 2% | 18% | 7% | 37% | 2% | 2% | 0% | 6% | 19% | 2% |
| Vendetta t+1 | 198 | 12% | 6% | 7% | 20% | 14% | 6% | 1% | 1% | 4% | 28% | 4% |
| VesperVale t0 | 9 | 56% | 0% | 0% | 22% | 22% | 0% | 0% | 0% | 0% | 0% | 0% |
| VesperVale t+1 | 9 | 33% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 56% | 11% |
| Willow t0 | 69 | 9% | 0% | 0% | 12% | 35% | 1% | 6% | 0% | 1% | 32% | 4% |
| Willow t+1 | 69 | 12% | 1% | 0% | 25% | 14% | 7% | 0% | 0% | 0% | 32% | 9% |

### OPPONENTS: by hp band before the hit (all hit rounds), action at t0 / t+1

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hp >70 t0 | 3875 | 19% | 3% | 8% | 7% | 29% | 4% | 2% | 0% | 5% | 23% | 0% |
| hp >70 t+1 | 3875 | 21% | 3% | 6% | 17% | 15% | 4% | 2% | 0% | 4% | 26% | 1% |
| hp 40-70 t0 | 2858 | 22% | 5% | 9% | 16% | 14% | 4% | 1% | 0% | 4% | 22% | 2% |
| hp 40-70 t+1 | 2858 | 20% | 6% | 6% | 31% | 8% | 5% | 1% | 1% | 3% | 16% | 4% |
| hp <40 t0 | 1361 | 11% | 8% | 3% | 21% | 4% | 4% | 0% | 2% | 2% | 19% | 27% |
| hp <40 t+1 | 1361 | 8% | 6% | 1% | 32% | 2% | 2% | 0% | 2% | 1% | 9% | 37% |

### OPPONENTS: by champion class x hp band, action at t+1 (all hit rounds)

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| melee hp >70 | 2462 | 17% | 5% | 9% | 17% | 17% | 4% | 1% | 0% | 4% | 25% | 1% |
| melee hp 40-70 | 1932 | 18% | 9% | 9% | 28% | 9% | 5% | 1% | 1% | 2% | 16% | 3% |
| melee hp <40 | 946 | 9% | 9% | 2% | 32% | 2% | 2% | 0% | 1% | 1% | 10% | 31% |
| caster hp >70 | 1338 | 29% | 0% | 0% | 17% | 13% | 5% | 3% | 0% | 4% | 27% | 2% |
| caster hp 40-70 | 862 | 23% | 0% | 0% | 37% | 5% | 6% | 2% | 2% | 3% | 16% | 7% |
| caster hp <40 | 392 | 6% | 0% | 0% | 30% | 1% | 2% | 0% | 3% | 1% | 7% | 51% |

### Rounds from the first hit of an episode to the first retreat step

Retreat step = a move that increases the distance to the nearest enemy and after which that distance is >= 2 larger 3 rounds later (or >= 1 with no attack). Only episodes in which the champion was hit by an enemy champion; "none" = no retreat step within the episode + 3 rounds.

| team | episodes | retreat within episode | delay 0 | 1 | 2 | 3 | 4-5 | 6-10 | >10 | median delay | episode died | died with no retreat step | died after a retreat step |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| us | 2866 | 62% | 252 | 377 | 365 | 283 | 262 | 219 | 17 | 2 | 717 | 349 | 368 |
| opp | 3450 | 58% | 264 | 459 | 468 | 261 | 244 | 244 | 47 | 2 | 474 | 308 | 166 |

By champion type and hp band at the first hit (us): share of episodes with a retreat step and median delay

| type | episodes | retreat | med delay | hp>70: n / retreat / delay | 40-70 | <40 |
|---|---|---|---|---|---|---|
| us Cassi | 327 | 61% | 2 | 250 / 61% / 2 | 64 / 66% / 2.0 | 13 / 46% / 0.5 |
| us Issac | 352 | 70% | 2.0 | 296 / 70% / 2.0 | 44 / 75% / 1 | 12 / 58% / 1 |
| us Prism | 197 | 46% | 3.0 | 154 / 45% / 3 | 36 / 50% / 3.0 | 7 / 43% / 2 |
| us Ren | 674 | 71% | 2 | 531 / 71% / 2 | 122 / 75% / 2.0 | 21 / 48% / 1.0 |
| us Ryth | 308 | 67% | 3 | 238 / 66% / 4.0 | 52 / 71% / 2 | 18 / 67% / 1.5 |
| us Stellar | 531 | 48% | 2 | 439 / 49% / 2 | 72 / 50% / 1.5 | 20 / 20% / 0.0 |
| us Tavi | 310 | 60% | 2.0 | 231 / 64% / 2 | 59 / 54% / 1.0 | 20 / 35% / 1 |
| us Varg | 73 | 66% | 2.0 | 57 / 67% / 3.0 | 13 / 77% / 2.0 | 3 / 0% / None |
| us Vendetta | 94 | 71% | 2 | 61 / 67% / 2 | 29 / 83% / 1.0 | 4 / 50% / 1.0 |
| opp Cassi | 381 | 55% | 2 | 285 / 53% / 2.0 | 76 / 67% / 1 | 20 / 30% / 1.0 |
| opp Issac | 604 | 64% | 2.0 | 456 / 61% / 2 | 120 / 79% / 2 | 28 / 43% / 1.0 |
| opp Marcella | 28 | 46% | 2 | 15 / 53% / 3.0 | 11 / 45% / 0 | 2 / 0% / None |
| opp Prism | 112 | 54% | 2.0 | 83 / 53% / 2.0 | 23 / 52% / 1.5 | 6 / 67% / 1.5 |
| opp Ren | 516 | 59% | 2 | 355 / 57% / 3.0 | 120 / 73% / 2.0 | 41 / 41% / 1 |
| opp Ryth | 335 | 61% | 3 | 231 / 59% / 3 | 79 / 70% / 2 | 25 / 52% / 1 |
| opp Stellar | 574 | 47% | 2 | 403 / 45% / 2.0 | 130 / 57% / 1.5 | 41 / 32% / 1 |
| opp Tavi | 317 | 52% | 2.0 | 231 / 48% / 3.0 | 73 / 64% / 1 | 13 / 54% / 1 |
| opp Varg | 307 | 64% | 2.0 | 228 / 61% / 3 | 67 / 78% / 2.0 | 12 / 42% / 1 |
| opp Vendetta | 198 | 67% | 2 | 145 / 64% / 3 | 46 / 80% / 1 | 7 / 43% / 1 |
| opp VesperVale | 9 | 56% | 2 | 4 / 25% / 4 | 5 / 80% / 1.0 | 0 / - / None |
| opp Willow | 69 | 58% | 2.0 | 48 / 56% / 2 | 20 / 65% / 1 | 1 / 0% / None |

Retreat alone or with the group (allies within 6 at the retreat step; an ally "also retreats" if its distance to the same enemy grows by >= 2 over the next 2 rounds)

| team | retreat steps | no ally within 6 | allies stay/fight | some allies retreat | all allies retreat |
|---|---|---|---|---|---|
| us | 1775 | 31% | 45% | 11% | 14% |
| opp | 1987 | 31% | 43% | 14% | 12% |

## Q2. Retreat quality

Unit = retreat step (as defined above), n us 1775, opponents 1987. "Foe follows" = in the next 12 rounds the nearest enemy (at the retreat step) made a move that reduced its distance to the retreating champion; chase length = last such round. Outcome within 15 rounds: death, recall arrived, escape (nearest enemy >= 8 and not hit in rounds 8-15), escape_near (not hit in rounds 8-15 but an enemy still within 8), still_fighting (hit again in rounds 8-15).

| team | n | hp% med | foe dist at step med | foe follows >=1 | >=3 steps | chase len med (if followed) | dist to foe +5r: med change | outrun (>= +3) | caught (<= 0) | toward spawn (dspawn -2 or more) | away from spawn (+2) | toward ally (-2) | away from ally (+2) | death | recall | escape | escape_near | still_fighting | recall started within 15r |
|---||---||---||---||---||---||---||---||---||---||---||---||---||---||---||---||---||---||---||---|
| us all | 1775 | 54 | 3 | 76% | 39% | 8.0 | 3 | 46% | 9% | 53% | 6% | 29% | 18% | 26% | 37% | 14% | 13% | 10% | 52% |
| us melee | 1043 | 54 | 3 | 76% | 42% | 8 | 3 | 53% | 9% | 61% | 7% | 33% | 19% | 20% | 40% | 17% | 12% | 11% | 55% |
| us caster | 732 | 52.0 | 3.0 | 77% | 35% | 7 | 2.0 | 36% | 9% | 41% | 5% | 22% | 17% | 35% | 33% | 11% | 13% | 8% | 48% |
| us hp >70 | 559 | 84 | 3 | 77% | 44% | 9 | 2.0 | 38% | 18% | 45% | 14% | 34% | 16% | 19% | 14% | 22% | 21% | 23% | 29% |
| us hp 40-70 | 643 | 54 | 3 | 75% | 41% | 8 | 3 | 52% | 8% | 58% | 4% | 34% | 19% | 21% | 44% | 16% | 13% | 7% | 61% |
| us hp <40 | 573 | 27 | 2 | 77% | 32% | 5.0 | 4.0 | 47% | 2% | 54% | 1% | 17% | 20% | 40% | 52% | 4% | 3% | 1% | 65% |
| us vs melee foe | 1012 | 52.0 | 2.0 | 78% | 41% | 7.0 | 3 | 48% | 7% | 52% | 6% | 28% | 17% | 29% | 34% | 14% | 12% | 11% | 46% |
| us vs caster foe | 741 | 55 | 3 | 74% | 37% | 8 | 2 | 43% | 12% | 54% | 6% | 30% | 19% | 23% | 40% | 14% | 14% | 9% | 60% |
| opp all | 1987 | 49 | 3 | 72% | 38% | 9 | 4.0 | 60% | 7% | 63% | 9% | 29% | 23% | 13% | 47% | 15% | 13% | 12% | 61% |
| opp melee | 1240 | 50.0 | 3.0 | 72% | 37% | 9 | 4 | 62% | 7% | 64% | 10% | 33% | 22% | 13% | 45% | 15% | 12% | 14% | 60% |
| opp caster | 702 | 45.0 | 4.0 | 71% | 41% | 9.0 | 3 | 56% | 7% | 61% | 7% | 24% | 23% | 13% | 49% | 15% | 13% | 10% | 62% |
| opp hp >70 | 456 | 82.0 | 3.0 | 71% | 39% | 9 | 2.0 | 48% | 12% | 49% | 15% | 28% | 22% | 8% | 19% | 24% | 21% | 28% | 34% |
| opp hp 40-70 | 808 | 53.0 | 3.0 | 72% | 39% | 9 | 4 | 61% | 8% | 63% | 9% | 34% | 20% | 12% | 44% | 17% | 14% | 13% | 59% |
| opp hp <40 | 723 | 27 | 3 | 71% | 37% | 8 | 4 | 67% | 3% | 72% | 4% | 24% | 27% | 17% | 69% | 7% | 6% | 2% | 80% |
| opp vs melee foe | 971 | 49 | 2 | 75% | 40% | 9 | 4 | 60% | 6% | 61% | 10% | 29% | 22% | 15% | 44% | 14% | 13% | 14% | 59% |
| opp vs caster foe | 1016 | 49.0 | 3.0 | 68% | 37% | 9.0 | 3 | 61% | 7% | 65% | 8% | 29% | 24% | 11% | 50% | 16% | 12% | 11% | 63% |

Us: retreat outcome by map / result / opponent tier / champion type

| split | n | hp% med | foe follows | death | recall | escape(+near) | still fighting | recall started |
|---|---|---|---|---|---|---|---|---|
| map collision | 421 | 51 | 82% | 22% | 42% | 27% | 9% | 56% |
| map corners | 490 | 50.5 | 72% | 35% | 37% | 16% | 12% | 55% |
| map elkring | 155 | 50 | 72% | 28% | 42% | 25% | 5% | 54% |
| map expanse | 11 | 71 | 73% | 0% | 45% | 55% | 0% | 45% |
| map interlock | 159 | 67 | 77% | 16% | 31% | 38% | 14% | 49% |
| map lanes | 176 | 50.0 | 74% | 19% | 31% | 40% | 10% | 41% |
| map monolith | 108 | 57.0 | 83% | 23% | 24% | 40% | 13% | 36% |
| map packs | 249 | 57 | 76% | 29% | 39% | 25% | 7% | 55% |
| map rows | 6 | 71.0 | 67% | 17% | 0% | 83% | 0% | 17% |
| result win | 595 | 56 | 74% | 19% | 39% | 32% | 10% | 52% |
| result loss | 1180 | 53.0 | 77% | 30% | 36% | 24% | 10% | 52% |
| opp top10 | 668 | 56.0 | 79% | 27% | 37% | 25% | 12% | 54% |
| opp 11-20 | 593 | 51 | 76% | 24% | 38% | 27% | 10% | 51% |
| opp 21-30 | 507 | 52 | 73% | 29% | 35% | 29% | 7% | 50% |
| opp other | 7 | 48 | 71% | 0% | 43% | 57% | 0% | 57% |
| Cassi | 201 | 49 | 82% | 32% | 34% | 28% | 6% | 48% |
| Issac | 246 | 56.5 | 82% | 22% | 40% | 28% | 10% | 54% |
| Prism | 90 | 46.0 | 71% | 47% | 30% | 18% | 6% | 44% |
| Ren | 477 | 56 | 75% | 18% | 43% | 27% | 12% | 57% |
| Ryth | 205 | 48 | 67% | 26% | 36% | 27% | 12% | 58% |
| Stellar | 255 | 54 | 82% | 33% | 37% | 24% | 6% | 49% |
| Tavi | 186 | 57.0 | 68% | 36% | 28% | 23% | 13% | 46% |
| Varg | 48 | 59.5 | 79% | 8% | 29% | 52% | 10% | 33% |
| Vendetta | 67 | 50 | 79% | 16% | 37% | 36% | 10% | 52% |

Examples (us): retreats that ended in death: 64d3af95 corners Ryth r498 hp62% foe Ryth at 2; 64d3af95 corners Ryth r598 hp58% foe Ren at 1; 64d3af95 corners Prism r540 hp66% foe Issac at 3; 64d3af95 corners Ren r365 hp58% foe Varg at 2; 64d3af95 corners Tavi r335 hp53% foe Cassi at 1; 64d3af95 corners Tavi r559 hp52% foe Varg at 1; 7ba9fe5c packs Cassi r415 hp100% foe Vendetta at 3; ca10ce5a elkring Stellar r537 hp92% foe Ryth at 2; ca10ce5a elkring Ren r517 hp50% foe Vendetta at 1; 14ebd970 rows Issac r111 hp58% foe Vendetta at 2; d97caaff elkring Tavi r67 hp51% foe Ren at 4; 40eab0a2 monolith Vendetta r419 hp90% foe Varg at 1; 5889b79f packs Cassi r186 hp60% foe Ren at 1; 5889b79f packs Issac r178 hp58% foe Stellar at 2; 95784669 collision Issac r34 hp52% foe Stellar at 1; 95784669 collision Issac r361 hp60% foe Ren at 1; 7650c0e0 packs Ren r134 hp70% foe Stellar at 4; 7650c0e0 packs Ren r429 hp63% foe Ryth at 2; 69757c8e collision Cassi r862 hp76% foe Issac at 2; 69757c8e collision Issac r272 hp49% foe Cassi at 3; 69757c8e collision Issac r555 hp81% foe Ren at 4; 69757c8e collision Ren r132 hp93% foe Stellar at 4; 69757c8e collision Ren r868 hp100% foe Stellar at 4; 69757c8e collision Stellar r745 hp73% foe Issac at 1; 697

Examples (us): retreats saved by recall: 79bed885 collision Cassi r258 hp21% recall after 6 rounds; 79bed885 collision Issac r213 hp48% recall after 7 rounds; 79bed885 collision Stellar r468 hp76% recall after 9 rounds; 64d3af95 corners Ryth r208 hp48% recall after 6 rounds; 64d3af95 corners Ryth r261 hp32% recall after 3 rounds; 64d3af95 corners Ryth r314 hp27% recall after 8 rounds; 64d3af95 corners Stellar r271 hp64% recall after 6 rounds; 64d3af95 corners Stellar r316 hp52% recall after 6 rounds; 64d3af95 corners Stellar r450 hp32% recall after 4 rounds; 64d3af95 corners Stellar r507 hp35% recall after 4 rounds; 64d3af95 corners 
