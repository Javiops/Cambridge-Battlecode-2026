# Stack or spread, and idle champions (15-10-2026)

Question: when should several champions farm one camp, and when should they spread out? And should a champion
that is waiting ever stand still?

All tests use `tools/ab.py` (team repo PR #2) against the same bot without the change. A map counts only when one
bot wins it from both sides.

## The answer: decide per camp, by its size

- **Big camps (3000+ hp): stack.** These are 2-3 elks, an elk with wolves, or 3 wolves, about 1 camp in 4.
  Up to 4 champions go there. A champion joining values the camp at `gems / team^0.75` instead of `gems / team`.
- **Small camps (under 3000 hp): spread.** These are single wolves or elks, 2 wolves, and gem clusters.
  One champion each (a pair on gem clusters, as before).

What the bot does differently with the rule (106 games, official + 44 generated maps):

| | champions per kill, small camps | rounds per kill, small | champions per kill, big camps | rounds per kill, big | big camps killed |
|---|---|---|---|---|---|
| study26 | 1.40 | 11.6 | 2.02 | 26.7 | 207 |
| study26 + rule | 1.43 | 11.6 | 2.42 | 21.5 | 264 |

Results (maps won both sides / lost both sides):

| bot | official 9 | gen 44 | hold 60 | dev 200 | v100 | f150 (made after tuning) | all |
|---|---|---|---|---|---|---|---|
| study25 + rule (exp 0.75) vs study25 | 3/2 | 11/7 | 21/7 | 57/37 | 28/22 | 34/27 | 154/102 |
| **study26 + rule vs study26** | 2/1 | 14/7 | 20/9 | 54/43 | 26/20 | 38/26 | **154/106 (p < 0.01)** |

Where the line sits:

| variant (vs study25) | all sets except f150 |
|---|---|
| threshold 2400 hp (single elks and wolf pairs stack too) | 125/120, the gain is gone |
| threshold 3000 hp, exp 0.5 | 125/88 |
| threshold 4000 hp, exp 0.5 | 118/85 |
| threshold 3000 hp, exp 0.25 (stack harder) | 107/100 |
| threshold 3000 hp, exp 0.75 | 120/75, positive on every set |
| Mite's measured squad rule taken literally (2 on every small camp, 4 on big) | 68/138, loses clearly |
| only the big-camp half of it, valued at gems/4 | 82/81 and 43/53 |
| whole team on the first camp before round 50 | 89/75, no clear gain; on top of the rule 120/111 |

Map-level features do not tell when stacking pays. That includes camps per champion, spacing between camps, and
mean camp hp. A split that looked good on hold60 and dev200 (few camps per champion, or big camps) reversed on the
100 extra maps. The size of the camp being chosen is what matters.

## Idle champions

- Our champions do not wander. On the online games against Mite, 2-5% of steps did not bring a champion closer to
  its next camp, for both teams. What looks "lost" is standing.
- Standing next to a camp that is about to respawn is 11% of champion turns. Rally waits are under 1%.
- Three ways of never waiting all lose clearly: P_NOIDLE 0 / 2 / 5. With them, a waiting champion joins another
  camp or walks to one that is up. Results: 45/131, 40/127 and 52/120 maps.
  The waiting champion is already where the next capture will be. Leaving costs that capture and turns the wait
  into walking: approach turns go from 16% to 28%.

## Files

- `bot/mybot_study27.zip` = study27 = study26 + the rule (`P_MAX_SHARE 4`, `P_SHAREEXP 75`, `P_STACK_HP 3000`).
  It is the same binary as `bot/mybot_study26_stack.zip` (source `bot/study26_stack/src`). In the team repo it is
  `bots/study27`. The change is one line in `choose_target` plus two defaults.
- The study25-based variants and switches (P_MSQUAD, P_NOIDLE, P_SHAREEXP, P_STACK_HP) are in
  `bot-st25-card/src`, all off by default.
