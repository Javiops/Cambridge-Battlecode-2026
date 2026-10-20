# Roadmap

Open questions and the next steps, in order. Settled conclusions move to DECISIONS.md.

## Stage 1 of the seven-stage learning plan: complete

The October 20 official runtime, persistent actor stepping/batching, generated map pools,
five-control calibration, release inference fuel and observation/action parity are verified.
See [STAGE1.md](STAGE1.md), `results/stage1-*.json` and the executable acceptance command
`python -m lab stage1 ready`. Confirmation games remain unplayed.

## Stage 2: first baseline dataset complete

The immutable 24-slot plan produced 23 clean games and one quarantined fuel-limited v76
mirror. There are 104,133 sampled frames: 44,221 eligible train and 15,070 eligible
validation examples. Whole maps, families and both teacher/opponent lineages are disjoint.
Twenty new live sparring replays remain separate diagnostics. See STAGE2.md and
`results/stage2-*.json`; final confirmation maps remain sealed.

## Stage 3: first behavioural cloning model complete

`bc-v1` fits the certified 305-parameter model with class-aware training and a whole-map
development split inside training. Its one final held-out evaluation scores 63.39% exact
candidate accuracy against 56.91% constant wait, and 72.98% macro action recall. The
untrained control scores 73.28% exact accuracy but only 0.73% movement-type recall;
the trained actor has 73.51% movement-type recall and predicts too many casts.
See STAGE3.md for all per-action metrics, 1,440-turn bit-exact release parity and 24
paired diagnostic matches. No promotion, live upload, confirmation play, or Stage 4 run.

The first model is a warm start, not a competitive submission. It banks no gems because
the local proposal contract has no submission action. Future work needs macro/action
coverage and stronger in-engine learning, with fresh evaluation data for any new tuning.
Willow/Heart are absent from the dataset; cast imitation has no validation labels.

## Foundation (before any real bot)

1. **Map generator: complete.** The immutable g1 manifest covers 100 screen and 60 generated
   holdouts. The 2,500-game current-patch calibration places both handicaps below starter;
   the seed gap is 16 points. The 10% handicap remains subject to overlapping bootstrap intervals.
2. **Noise floor as a number in every report.** Run the seed twin in every league and print its gap to
   starter next to the leaderboard, so every result is read against it.
3. **Farm benchmark.** Each version against `dummy-v1`: banked gems at rounds 500/1000/1500 and the round it
   reaches 1000. No opponent means no fight noise. It is a diagnostic for the economy, never the promotion judge
   (Carson, kaggriculture: outcome targets beat shaped proxies).
4. **Ladder replays as opponents' teacher.** Later: download top-team replays and measure their curves
   with the same snapshot fields, so our numbers have a target.

## The bot (after the foundation)

Layers: `sense -> plan -> act -> log`, strategy as data tables picked from map features.
Phases: economy, survival and fights, team play, freeze on 2 November.
