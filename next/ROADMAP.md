# Roadmap

Latest checkpoint: **v93 / topdraft v19 compiled and live;all50groups/250games complete native-verified**:79wins versus77,zero faults,one unchanged fuel event. All250seeds equal;228/228ordinary controls exact. Sole22bank306.05→363.5,fresh322.55→383.64,deaths49.45→47.45;full first-cycle release22→21,no-fresh4unchanged. Next inspect post-rally execution in the four unchanged zero-fresh cases. See V93-FIELD.md,objective-execution-investigation.md and CURRENT.json.

Historical checkpoint: **v92 / topdraft v18 compiled and live**,all50 groups/250 games complete native-verified:77wins,0faults,1fuel. Matched v91:46/140 versus49. Shared release fixes traced Stellar join176;objective metrics remain separate from wins. All actual1.0.1. Next: test a16-round limit from first receipt for propagated joins,with unchanged local quorum and survival/banking rules;see experiments/shared-release-age-hypothesis.md. See V92-FIELD.md and CURRENT.json. Older checkpoints are historical.

Historical checkpoint: **v91 / topdraft v17 compiled and live**,all28 requested groups/140 games complete native-verified:49wins,0faults,1 exhausted turn. Matched v90 subset35/110 versus32.16 remaining planned groups were not requested. Five traced teammates release while Stellar still waits; next test a shared release decision after byte-role audit. All games actual1.0.1;1.0.2 announcement is separate. See V91-FIELD.md and CURRENT.json. Older checkpoints below are historical.

Historical checkpoint: **v90 / topdraft v16 compiled and live**,22 requested groups/110 games complete native-verified:32wins,0faults,1 exhausted turn on35maps. Other22 planned groups were not requested. Earlier rally still leaves split squad releases; inspect quorum visibility and per-unit release latch. New1.0.2 is announced; these games are actual1.0.1. See V90-FIELD.md and CURRENT.json; older status statements below are historical.

Current checkpoint: **v89 curriculum complete**,71/220 wins,0 faults,1 exhausted turn on35 maps. Matched v88 subset7/30 versus8/30. Eight nonleader elk opponents collect fresh gems before our350 rally; next test earlier timing with generated geometry controls. Later quota check observes6 available. See V89-CURRICULUM.md and CURRENT.json; older live-status statements below are historical.

Open questions and the next steps, in order. Settled conclusions move to DECISIONS.md.

Current status: Stage 7 qualification is complete. Statements below about sealed
confirmation maps describe earlier stage milestones; both final cohorts are now consumed.

## Current development after deployment

- V89 / topdraft v15 is compiled and live. Its single-snapshot cover scan skips
  hidden entries without abandoning later visible allies. Exact local rebuild,
  server source/build and actual queued versions are verified. The first matched
  30 field games bank600 from800 collected on Cozy contest, versus v88 200/800;
  wins are7/30 versus8/30. Full44-group /220-game curriculum is requested on35
  maps; finish collection/native audit. See V89-CURRICULUM.md and SCAN-V15.md.
  Lower aggregate wins alone do not undo the functional correction. Diagnose
  acquisition, fight exposure and sustained objective damage separately next.

- V88 / topdraft v14 is compiled and live; server source delivery and build log
  are verified. Verify every queued version, then
  use returning unranked quota with the pinned cover-live-plan.json pairs.
  V14's quiet channel cover passes 69/70 starter, 149/302 live v12 and 160/302
  fixed v6, zero faults and six fuel losses per schedule. V13's unfiltered scan
  regresses farming and stays rejected offline. See COVER-V14.md. No promotion.

- Platform **v87 / topdraft v12 is compiled and live**, retaining v8 banking and checking contact before ally scans. The paired v85/v86/v87 banking benchmark is complete: 30 native-verified games, each version 5/10 with zero faults/fuel losses. Big-world deposits improve; elk B acquisition regresses. See BANKING-FIELD.md and CONTACT-V12.md.

- Continue the hourly unranked curriculum: most opponents near/moderately above
  our strength, with a repeatable benchmark and at most 10% leader scouting.
- The teammate handoff was honored through 23:10:20 UTC on 20 October and their
  batch completed before resuming. Read LIVE-HOLD.json for that historical record
  and CURRENT.json for the current selection; honor any new handoff.
- V7 fixes the reproduced large-load banking stall locally: big-world versus
  starter deposits rise from 121/0 to 316/105, both seats, zero faults/fuel losses.
  It wins 148/302 versus v6 across broad development maps; no promotion claim.
- V8 finishes small already-started trips early: local starter deposits 692/800
  on big-world, zero faults/fuel losses in both seats. Broad fixed-v6 comparison
  is 146/302 and 14 fuel losses; parent-v7 comparison is 152/302 and 106 losses.
  A generated B-seat fixture accounts for 94 losses with either v7 or v8.
  The v9 optional spell-scan entry guard leaves those 94 unchanged and is rejected.
- All 44 broader v87 curriculum groups / 220 games are complete and
  native-verified across all 35 maps: 75 wins, zero faults, one fuel loss.
  The historical same-label v83 subset has 87 wins and 70 fuel losses; opponent-B
  and seed equivalence are not certified. Overall results regress despite runtime
  improvement. Final actual allowance is zero. See V87-CURRICULUM.md, then trace
  carrier/fight exposure and isolate one general fix. Check allowance every 15
  minutes with the existing heartbeat. Historical cohort labels overlap current
  ratings; adapt difficulty using measured results.
- Profile optional native calls on big-world and ambush if fuel losses recur. The historical 250-game v83 batch
  has 55 and 41 fuel losses respectively. Raising the global reserve in v5
  stalled initialization; do not repeat that attempted fix.
- Elk-arena, big-world and pilgrimage each lose 0/6 against three nearby teams.
  Diagnose objective commitment, low collection and fight exposure separately.
  Pilgrimage averages 47.5 team deaths; collection/deposit differences alone
  do not prove a banking bug.
- After healthy allies assemble, test sustained single-objective damage and
  reward collection. Preserve ordinary multi-camp performance and both seats.
- Heart's copied focus build was isolated in v4 and lost 95/270 against v3.
  Repeating that purchase order without a new hypothesis is not the next step.
- Identify other one-area layouts from public metadata and replays; Fran does
  not have map names. The strict single-gem-group detector currently covers
  Stampede and elk-arena only.

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
paired diagnostic matches. No promotion, live upload or confirmation play.

The first model is a warm start, not a competitive submission. It banks no gems because
the local proposal contract has no submission action. Future work needs macro/action
coverage and stronger in-engine learning, with fresh evaluation data for any new tuning.
Willow/Heart are absent from the dataset; cast imitation has no validation labels.

## Stage 4: outcome critic acceptance complete

`outcome-v5` passes `stage4 ready`. Current native inventory and monotone team/economy
features improve both proper scores on 24 fresh games/eight unseen family-3 maps:
Brier 0.12508 versus 0.13067,
log loss 0.38629 versus 0.40075.
The paired map bootstrap interval supports the Brier improvement. See STAGE4.md for
training-only selection, provenance, calibration, the failed v1-v4 trials and limitations.
The BC actor is unchanged; final confirmation maps remain sealed.

## Stage 5: first PPO run trained; strength gate passed

`ppo-v1` starts from `bc-v1` and accepted `outcome-v5`, recalibrates its critic on
on-policy data, and completes 12 clipped PPO iterations. The native pipeline is audited.
Fresh matched-controller evaluation scores 60.94% on 64 games/16 maps;
90% whole-map interval [53.12%, 68.75%]. Stage 5 clears its native training and held-out strength milestone.
See STAGE5.md for the shared controller, duplicate self-play capture accounting,
source-bound old-policy checks, model hashes and remaining coverage limits.

## Stage 6 C++ runtime complete

The unchanged PPO checkpoint and controller pass exact native parity for 262,936
decisions/160,000 turns in 16 full release matches. All six physical champion types,
both seats, banking and maps up to 80×80 are covered. Official total fuel peaks at
84,574/100,000 on ordinary turns and 97,603/200,000 on first turns. There are no faults
or fuel losses, and the source bundle reproduces the frozen WASM. See STAGE6.md and
`python -m lab stage6 ready`.

## Stage 7 competitive qualification complete

`ppo-league-v12` combines the expert strategic controller with the unchanged PPO weights.
It wins 200/200 screening games and 140/140 fresh confirmation games
against starter. The unchanged promotion gate passes with zero bot faults and
0.0000 fuel-exhausted turns/game (limit 1.0); the source ZIP rebuilds
exactly. The actor-disabled control also wins all screening games, so no independent
PPO strength gain is established. See STAGE7.md and `python -m lab stage7 ready`.

Both the original v11 confirmation cohort and replacement v12 cohort are now
consumed. Preserve their attempt locks. Further tuning needs fresh holdouts.
The seven-stage first pass is complete; no live upload or champion change was made.
Next: review the qualified source bundle, then explicitly authorize upload and
evaluate stronger opponents using a new independent test plan.

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
