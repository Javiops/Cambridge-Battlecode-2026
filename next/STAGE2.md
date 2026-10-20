# Stage 2: baseline demonstrations

The first baseline dataset is collected and audited. `python -m lab stage2 ready` is
the admission check. Stage 3 training has not started.

## What was collected

The frozen local plan schedules 24 complete release games on eight generated screening
maps, with both seats together in one partition. It was written before these match
outcomes were inspected. Training uses two maps from each g1 family 0/1/2; validation
uses two different maps from family 3. Both the teacher and opponent lineages are
disjoint across partitions.

Training teachers are current-runtime rebuilds of the team's active v76 source
(`BASELINE V3 + TEAM-FIGHT ACCEPTED`). The original account archive and its hash are
preserved; `bots/baseline-online-v76/ORIGIN.json` identifies the submission. The copied
strategy is unchanged. It plays itself and the frozen idle reference. Idle turns are
retained as context but never become behavioural-cloning teacher examples.
Validation uses the SDK starter and its seed twin as one separate lineage. This is
deliberately a distribution-shift validation set, not a random split of nearby turns.

| Partition | Admitted games | Sampled decisions | Eligible BC examples |
|---|---:|---:|---:|
| Train | 17 | 72,763 | 44,221 |
| Validation | 6 | 31,370 | 15,070 |
| Total | 23 | 104,133 | 59,291 |

One planned v76 mirror game on `g1-screen-004` lost one team-B turn to fuel exhaustion.
It is quarantined as an entire episode, with no training labels. It remains visible
in the 24-slot manifest and original statistics. A failure in a paired non-mirror
comparison would quarantine both seats. Quarantine does not silently remove a
scheduled game or repair its outcome. All admitted games have zero faults and fuel
exhaustion, and all eight reserved maps still contribute clean data.

The complete trajectories remain in raw replays. Demonstration shards sample the whole
turn every fifth round, starting at round 1, independently of outcomes. Every sampled
native action is retained, including macro actions outside the micro-policy proposal
set. Model tensors contain only alive, qualified-teacher rows with a supported candidate
and one of the first two micro decisions of that turn. No unsupported action is relabelled
as wait. The current capsule includes 203 supported cast examples; most spell types
remain outside the Stage 1 proposal set.

## Actor and label integrity

`lab/replay.py` decodes the pinned native serializer's input records. It rejects unknown
tags, truncation, trailing bytes, incompatible headers and embedded-map mismatches.
`lab/replay-engine.mjs` replays those inputs with the exact official rules WASM and
queries each acting champion's authenticated perspective **before** its action. It
streams forward across input boundaries; repeatedly seeking from the beginning is
avoided. Completion and final banks must agree with the official release statistics.

The importer is independently checked against the Stage 1 SDK logs: all 2,560 actor
frames across four complete matches agree on features, masks and movement, and every
decoded accepted action agrees with the logged SDK action sequence. See
`results/stage2-replay-proof.json`.

The official replay does not serialize guest private RAM, shared-memory writes, or the
boolean returns of movement/cast calls. Missing shared memory is stored as **null**,
never invented as zero. Native accepted-input status is recorded; unavailable boolean
returns remain null. The certified v1 feature encoder consumes none of these unavailable
fields. This dataset supports that feed-forward contract, not imitation of the teacher's
private memory or recovery of every rejected SDK call.

Each episode fixes map, runtime/SDK, both WASM identities, lineage, seat and terminal
provenance. Each decision records actor/round, native input index, decision and micro
indices, scoped observation, candidates/mask, original action, candidate label and
eligibility. Episode identifiers connect rows to provenance without copying future
outcomes into actor features. Partial games, fuel-failed episodes and parser failures
cannot produce admitted outcome labels.

The audit recomputes every saved encoding, checks candidate labels and masks, compares
each eligible tensor to its original actor row, verifies shard hashes and counts, and
checks partition leakage. Use the manifest-based `shards()` loader, not a directory glob
that could accidentally include pilot or quarantined data.

## Live sparring evidence

Twenty newly requested unranked games used the existing active v76 bot, ten screening
site maps and both seats. Each reverse-seat group pins the opponent version from its
first group. Four of the team's 50 hourly match-group slots were used. The active
submission and ranked settings were unchanged; no `01*` confirmation maps were played.

| Opponent | Games | v76 wins | Mean round of loss | Mean gold: v76 / opponent | Deaths: v76 / opponent |
|---|---:|---:|---:|---:|---:|
| Nyx | 10 | 0 | 1,104 | 2,627 / 9,189 | 181 / 60 |
| Sneaky Bush Campers | 10 | 0 | 1,145 | 2,756 / 8,603 | 293 / 19 |

Gold is lifetime earned gold from the replay statistics; death totals cover ten games
per opponent. These measurements expose both an economy gap and severe survival problems
in some maps. They do not establish which code change would improve the bot.

All twenty native replay terminals match the website's observed winner, round and banks.
Their original downloads omit exact server-build and opponent-WASM identities, so they
are kept as `external_diagnostics`, outside the strict training/validation partitions.
This also prevents the v76 lineage in those games from leaking into validation.
See `results/stage2-online.json` for archive/replay hashes and individual match links.

## Files and reproduction

Install `requirements-data.txt` (CLI 3.0.1, pytest 9.1.1, NumPy 2.5.4), Node.js 22+ and
the pinned engine asset described in STAGE1.md. Generated maps and frozen references
are the same reproducible local artifacts as Stage 1.

```bash
# Run in next/; freeze only if this name does not already exist.
python -m lab freeze bots/baseline-online-v76 online-v76-week2-v1 --parent ""
python -m lab stage2 plan
python -m lab stage2 collect
python -m lab stage2 proof
python -m lab stage2 online
python -m lab stage2 audit
python -m pytest -q tests
python -m lab stage2 ready
```

`online` reads the four downloaded match-group archives in
`datasets/stage2-v1/raw/online/`. Download their original games through the signed-in
match links in the saved report, or use the delivered data archive. It never reads
browser cookies or creates more matches automatically.

`datasets/stage2-baseline-v1/plan.json` and `manifest.json` are immutable local artifacts.
Each episode has raw replay/statistics, provenance, compressed JSONL decisions and a
compact `bc.npz`. Large data stays outside Git; compact plans, hashes and audit reports
are committed. A delivered ZIP carries the actual shards and raw evidence.

```python
import numpy as np
from lab.dataset import shards

for episode, path in shards("train"):
    with np.load(path, allow_pickle=False) as batch:
        features = batch["features"]       # N x 24
        candidates = batch["candidates"]   # N x 16 x 12
        mask = batch["mask"]               # N x 16
        action_label = batch["label"]      # N, each label has mask=True
        # team/input identify the original decision; win is a separate critic target.
```

## Stage 3 handoff and limits

The train action counts are wait 23,698; move 15,572; attack 4,748; cast 203. Validation
has wait 8,576; move 3,405; attack 3,089, with no supported cast examples. A constant-wait
classifier already reaches **56.9% validation accuracy**. Report per-action results,
balanced metrics and an official match evaluation; raw accuracy alone is insufficient.

Training covers seven champion body types; validation covers eleven. Willow and Heart
of Ruin are absent from this first dataset. Training win labels are also skewed by idle
opponents (36,320 wins / 7,901 losses). Preserve this limitation for the later critic.
Do not claim universal champion coverage or strong-opponent qualification.

Next: train the small behavioural-cloning model against this frozen dataset, with the
validation partition untouched by fitting and class imbalance handled explicitly. New
spells, features, memory inputs or a larger model need updated collection coverage and
a fresh Stage 1 release fuel/parity certificate. No learned weights or training run are
part of Stage 2.
