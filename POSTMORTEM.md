# Postmortem: Live Love Larp, Cambridge Battlecode 2026a

Written 8 November 2026, after the 4 November international qualifier and before the 18 November finals.

## Summary

We did not reach the finals. Our goal was the top 10. Our best recorded ladder rank was 52 (24 October). On
8 November we were 125th of 826 with a rating of 1925, 87th in the international category. Our final bot, v21, won
**7 of 80** games against ladder ranks 5 to 20.

In one sentence: **we spent four weeks testing hundreds of small pieces on a base that died twice as often as the top
teams, and we could measure almost none of them reliably.** The gap to the top was not a missing rule. Our champions
died alone in our own half between rounds 150 and 300, and we never fixed that at the root.

## Rating over the season

| Date | Rating | What happened |
| --- | ---: | --- |
| 13 Oct | 1500 | First upload |
| 18 Oct | 1728 | v53 base, online judge starts |
| 21 Oct | 1649 | Low point after the week 2 balance patches |
| 23 Oct | 1856 | goldval, horfocus and stallfix go live: +207 in two days |
| 26 Oct | 1875 | Patch 2.0.0 (every champion rebalanced, 35 to 70 maps) |
| 31 Oct | 1876 | v21 live in ranked since 30 October |
| 4 Nov | 1908 | International qualifier (top 8 international teams only) |
| 8 Nov | 1925 | Ladder still open; this no longer counts |

## Timeline

The project changed method five times in three weeks, and each change threw away most of what came before.

| Dates | Phase | What we did | How it ended |
| --- | --- | --- | --- |
| 13-14 Oct | First bot and switches | C++ bot, top-5 and top-10 replay studies, each top-team habit coded as a `P_*` switch | Many won locally and lost online (P_HOLD went 0-7 on corners and collision) |
| 15 Oct | Top-2 dissection | Decision-by-decision study of the top 2 teams; study26 to study28 | Their edge was dying less, not fighting better. study28 went 24-5 locally and was flat online |
| 16 Oct | Genetic algorithms, DQN, imitation | 7 cloud islands plus a PC, Q-learning, cloning the top team's fights | Dropped. The genetic "champion" was selection luck |
| 16-17 Oct | Teammate base, v52 to v59 | Behaviour fixes, fight verdict, two-sided fight model, wards | v53 became the base. v54 to v59 were rejected online; lanes collapsed from fuel overruns |
| 17-18 Oct | From-scratch lab | New bot with a local league, ratings and gates | Ranked 27th of 28 against our old bots: the lab measured against rivals that were too weak. Back to v53 |
| 18-24 Oct | Online loop | Online judge at 50 match groups per hour; candidates for defence, banking, micro, kills, pairs, shop, farm | A few passed (bank-v1b, recall escape, team fight). On 24 October, 16 candidates and none passed |
| 25-27 Oct | Deterministic base | Fixed fuel metering so a code change stops reshuffling games; engine patch 2.0.0 | Every farm-pricing, superiority and shop piece was closed: none passed online |
| 27-30 Oct | Copy the top-10 plan | Per-map, per-50-round plan from 600 top-10 vs top-10 games; escort roles | v21 passed the bar over 400 games (+21 net vs the base) and went live on 30 October |
| 4 Nov | International qualifier | Only the top 8 international teams qualified | We did not qualify |

The game also changed underneath us: three balance patches in week 2 and the large 2.0.0 patch on 25 October.
Each one made part of what we had measured obsolete.

## What worked

What raised our rating were fixes to broken behaviour and changes that made us die less, not cleverer fight rules.

| Change | When | What it did | Measured result |
| --- | --- | --- | --- |
| goldval (v96) | 21 Oct | Stop chasing gold-only camps before round 940 | Deaths per game 9.9 to 7.5; +16 online |
| horfocus (v98) | 21 Oct | Focus build for Heart of Ruin, like the top 10 | Deaths in losses 11.0 to 6.7; +12 online |
| stallfix (v105) | 22 Oct | Remove stuck and idle champions | +11 online |
| bank-v1b (v65) | 18 Oct | Do not switch altars halfway through a banking trip | 17 for, 4 against in the games that changed |
| recall escape, team fight | 19 Oct | Recall to escape; team finishing layer | Promoted to base |
| P_MONO | 16 Oct | Fix for 0 gems on the contest map | Bug closed |
| Fuel fixes | 13, 17, 25 Oct | Turns cut off for exceeding the budget (lanes, wards, start-up work) | Lanes stopped collapsing |
| v21 (top-10 plan plus flee rules) | 30 Oct | Per-map plan and escort roles copied from the top 10 | +21 net over 400 games vs the base; without the flee rules, -6 |

Infrastructure also worked, but it arrived late:
- **Online judge on pinned games.** The engine is deterministic, so we could replay exactly the same match group with
  only the candidate changed and compare game by game.
- **Deterministic base (24 October).** Before it, any code change shifted fuel use and changed about 27% of games,
  which buried the real effect.

## What did not work, and why

Most of the work went into candidates that did not pass, almost always for the same reason: we measured against the
wrong thing.

1. **The local judge lied.** 0 of 8 local fight wins held online (review on 16 October). study28 went 24-5 locally and
   was flat online; P_HOLD won locally and went 0-7 online. Our local rivals were our own old bots, which never invaded
   in groups or punished mistakes.
2. **Uncontrolled noise for two weeks.** Before the deterministic base, any change moved fuel use and with it one game
   in four. A 70-game local panel was pure noise: near-identical tweaks ranged from 30-40 to 38-32. We made decisions
   on +-5 differences that meant nothing.
3. **Too many fronts at once.** On 16 October we ran 7 genetic islands, a DQN, imitation learning and three fix
   threads in parallel. On 24 October, 16 online candidates and none passed. An audit on 23 October found the code did
   what it claimed in 7 of 7 cases: what failed were interactions nobody checked.
4. **Machine learning without the game budget it needs.** Genetic algorithms, DQN, PPO and fight cloning produced
   nothing that held. Another team (777) reached the same result with 2.7 million training games.
5. **Changing method mid-race.** The from-scratch lab (17-18 October) was measured against rivals that were too weak
   and finished 27th of 28. That was two days without improving the ladder bot.
6. **Treating symptoms of the main gap.** From 18 October the diagnosis kept coming back the same: we die in our own
   half, outnumbered, between rounds 150 and 300 (1.8 deaths vs 0.6). We attacked it with separate pieces, and all of
   them failed online: half defence, regrouping, fleeing toward an ally, pairs, escorts, camp pricing, shop. None
   changed where the champions were, and with whom, before contact, which is what separated the top.
7. **Analysis errors.** The 27 October "jackpot" finding (1018 gems) came from summing group rewards wrongly. The old
   replay decoder had camp positions wrong on 18 maps. Several lines were opened on false numbers.
8. **Online quota as the bottleneck.** At 50 match groups per hour a candidate needed 2 to 4 hours for a reliable
   verdict. We spent that budget on many small candidates instead of a few large ones.

## How we compared with the top

Even fights were even. What separated us from the top was being together before contact, and through that dying less
and farming richer groups.

| Measure (source) | Top 5 or top 10 | Us |
| --- | --- | --- |
| Deaths per game, rounds 151-300 (top 5, 27 Oct) | 0.61 | 1.79 |
| Time with 2+ allies within 10 tiles (top 10, 27 Oct) | 60% | 48% |
| Opening captures with 3+ champions together, rounds 1-50 | 44% | 21% |
| Gems per capture, rounds 151-300 | 16 | 7 to 11 |
| Strong two-elk groups captured per game (vs ranks 56-70) | 0.7, with 3-4 champions and no deaths | 0.3, with 2-3 |
| Deaths in our own half (21 Oct) | About 50% of theirs | 67% of ours |
| Shop purchases after round 150 | 1.5 to 2 times more | Same gold in hand, lower income |
| Damage in even fights (677 fights, 18 Oct) | Equal | Equal |

[EvilMangohh](https://github.com/toyeshhm/cambridge-battlecode-2026), a team at our level (peak rank 22 before the
patch, 107th on 8 November), won 4 of 100 against the current top 10, close to our 7 of 80. They worked much like us,
with parallel agents, switches and a judge, and reached the same conclusions: local tests lie, merging changes hides
the bad ones, and what improves a bot is wasted turns and bugs found in replays. They did not close the gap either.

## Lessons for next time

1. **Day one: a reliable judge before ideas.** A deterministic engine setup (fixed fuel metering) and a platform
   benchmark against pinned versions of the strongest current rivals, compared game by game. We had this on 24-25
   October; it has to exist in week one.
2. **Local tests only check that nothing broke.** Never use them to decide whether an idea is good, least of all for
   fights.
3. **One method and one base for the whole competition.** No rebuild from scratch halfway. If the method changes, it
   changes on the same base.
4. **First stop dying, then everything else.** Fix bugs seen in replays of losses (stalls, recall loops, oscillation,
   fuel) and wasted turns. That is what gave us +200 between 21 and 23 October.
5. **Attack the structural cause with a design, not patches.** The gap was formation: where each champion is, and
   with whom, before contact. That needs a team plan from the draft (squads, roles, routes), not a rule that fires
   once enemies are already close.
6. **Few large candidates, one change at a time inside each.** With 50 match groups per hour there are about 12 tests
   a day; spend them on what could move 50 rating points, not 5.
7. **Check the numbers before opening a line.** Validate the replay decoder against the engine and check sums before
   building on a finding.
8. **No machine learning without the game budget it needs.** At most, CMA-ES on a few dozen constants of a rule bot.
9. **Study the top from day one and again every week.** The meta moves with every patch.
