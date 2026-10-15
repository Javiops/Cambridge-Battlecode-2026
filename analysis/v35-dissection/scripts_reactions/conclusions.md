## Observed rules of our bot when attacked (what a reader infers from the 150 games)

1. **There is no "I am being hit" reflex.** The action mix in the hit round (32% fight, 28% move, 20% nothing, 5% channel) is the same as the opponents' and the first retreat step comes a median 2 rounds after the first hit for both teams (us 62% of episodes retreat, opponents 58%). What differs is what happens before and after: we are hit at median 90% hp and still die in 25% of episodes (717/2866) vs 13.7% for the opponents.
2. **Melee walk in, casters stand and trade.** On the first hit Issac/Ryth/Varg/Vendetta step *closer* in 30-51% of cases (opponents' melee 35-38%, so similar), while Stellar/Prism fight back (34%/31%) and Tavi does nothing 43% of the time. Standing still while hit happens in 20% of all hit rounds; 689 of 3954 melee hit rounds (17%) are a melee standing still with the attacker 2+ tiles away (out of reach, not approaching, not leaving). 5-round idle streaks under fire exist (59ac9626 r182-186, cabfadde r251-255).
3. **Retreat threshold is ~50% hp, and the retreat is a 1-tile-per-round walk with the enemy adjacent.** Median hp at the retreat step 54%; the enemy follows in 76% of retreats and we outrun it in only 46% (opponents 60%). Retreats below 40% hp die 40% of the time (opponents 17%), casters' retreats 35%.
4. **Retreat alone.** 31% of retreat steps have no ally within 6, and in 45% the allies stay where they are; the group moves back together in 14%. We run toward spawn in 53% of retreats (opponents 63%), toward an ally in 29%.
5. **Recall is a teleport-home used from far away, not an escape.** 71% of the 3860 attempts start with no enemy within 9 tiles (99% arrive); only 15% follow a hit in the previous 3 rounds, and those arrive 67% of the time. hp at start is bimodal (30-40% heals, 80-90% repositions); there is no hp threshold (full-hp starts with no gems and no gold for every type). An interrupted recall is retried in 32% of cases and turned into a fight in 50%; Mite retries 59%.
6. **Channels are never cancelled.** 0 voluntary cancels of recalls (1 move-cancel in 3860 attempts); tributes continue with enemies walking into range 4 (17 deaths during a tribute channel, 724 gems; feb23cc4 r81, ae2470ab r805 where the tribute was even restarted at 14% hp).
7. **Allies help by shooting, not by moving, and only if they were not busy.** 29% of allies within 8 attack an enemy within 5 rounds, 20% move toward the victim; an ally that was hitting a camp keeps hitting it 46% of the time; a recalling ally never comes (7%). In 325 of our 709 direct deaths an ally was within 6 during the final episode and attacked nobody.
8. **We die at home, from full hp, to spells, over 4-8 rounds.** 73% of deaths in our own half, median 14 tiles from spawn; hp at the first hit median 90%; Stellar deals the killing blow in 30% of deaths and spells 68% of the episode damage; the final episode lasts a median 5 rounds, i.e. there were 4+ rounds in which a retreat or a recall at distance >= 6 was possible. 38% of victims were walking toward the enemy before the first hit.
9. **The 3-champion draft (cassi/ren/stellar) and corners are the worst.** 257 deaths in 57 three-champion games (4.5/game) vs 411 in 62 five-champion games (6.6/game, but 2 more champions); corners 13.5 deaths/game (230 in 17 games, 72% recall arrival), collision 7.9, elkring 6.5; expanse 0 and rows 0.1 (no fights there).

## Biggest differences from the opponents (pooled top-30) and from Mite

| behaviour | us | opponents (150 games) | Mite (reference) |
|---|---|---|---|
| deaths per game / gems lost per game / share of tributed | 5.72 / 57 / 7.1% | 3.87 / 57 / 6.3% | 4.9 / 52.5 / 5.7% (Univardisty 6.1 / 109 / 12.6%) |
| hit episodes ending in death | 25% (717/2866) | 13.7% (474/3450) | - |
| hp at first hit of the fatal episode (median) | 90% (501/709 >= 70%) | 72% (234/457 >= 70%) | 68% at r-5 (107/265 bursted) |
| deaths in own half / enemy half | 73% / 3% | 30% / 33% | median 15 tiles from spawn |
| victim walking toward the enemy before the fatal episode | 38% (270/709) | 45% (207/457) | - |
| retreat step hp (median) / retreats that die | 54% / 26% | 49% / 13% | 38% under fire / 16% |
| outrun the follower after 5 rounds (>= +3 tiles) | 46% | 60% | - |
| retreat toward own spawn | 53% | 63% | "walk away toward spawn" |
| retreat ends in a completed recall | 37% | 47% | 65-74% (hp < 50%) |
| recall attempts per game / arrival | 25.7 / 91% | 24-34 (spam merged) / 62-88% | 25 / 90% |
| recall started with a foe within 5 | 16% (49-66% arrive) | 14% | dfoe 7-8 in 35%, 1-5 rare |
| recall hp threshold | none (bimodal 30-40 / 80-90) | Tavi/Willow/Vendetta bots < 50% | strict heal < 50% |
| retry after an interrupted recall | 32% | 82% (incl. spam) | 59% |
| voluntary recall cancel | 0% | 2-3% | 0% (Univardisty 68 cancels) |
| ally within 8 helps (fights or comes) within 5 rounds | 49% | 49% | - |
| ally that was farming keeps farming | 46% | 40% | - |
| deaths with an ally within 6 that never attacked | 325/709 (46%) | 187/457 (41%) | - |
| deaths while a recall was in progress | 107 (15%) | 96 (21%) | 41 (15%) attempted in last 10 r |
| deaths during a tribute channel | 17 (724 gems) | 17 (930 gems) | - |
| killing blow by spell / top killer | 52% / Stellar 30% | 65% / our Stellar 36% | 62% / Stellar 34% |

The two numbers that explain the death gap: we take the first hit at 90% hp and still lose the champion in a quarter of the episodes, because the retreat starts 2 rounds later at ~50% hp, walks one tile per round with the attacker adjacent (outrun in 46%), goes to spawn only half the time and ends in a recall only 37% of the time; the opponents start their fatal episodes already damaged (median 72%), retreat toward spawn (63%), outrun (60%) and recall (47%). Against Mite the gap is in the recall discipline: Mite recalls at hp < 50% as soon as the nearest enemy is 7 tiles away and retries after every interruption (59%); we recall from 14 tiles away when nothing is around (71% of attempts) and, when hit at 4-5 tiles, we fight (50%) instead of retrying (32%).
