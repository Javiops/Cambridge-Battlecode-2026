# Stage 1: simulator and measurement contract

Stage 1 is complete for the pinned October 20 runtime. The acceptance command is
`python -m lab stage1 ready`; it checks the saved parity, calibration and throughput
proofs against current source, configuration, map and frozen-bot hashes. See
`results/stage1-ready.json`. Stage 2 data collection has not started.

## Runtime and maps

The official release runner remains the qualification oracle. Training uses the
**same official rules module**, through `lab/engine.mjs`, rather than an independent
implementation of combat or game rules. The module is distributed with the CLI's
map editor. Its SHA-256 is pinned in `lab.toml`; the adapter also checks its ABI
version. A patch requires a new pin and fresh differential/fuel proofs.

The Python `Environment` keeps one Node.js 22+ process alive and supports up to 64
independent episodes. Requests are JSONL, with ordered request IDs and bounded
timeouts. `batch_steps` returns an independent success/error result for every item.
Stale actor IDs, bad numeric inputs, closed games and invalid drafts fail explicitly.
The official scheduler owns turn order, channel progress, respawns and linked bodies.

`g1` generates 100 screening maps and 60 sealed confirmation maps, using disjoint
hash-derived seeds. Geometry is rotationally symmetric, includes all six camp types,
and varies size, terrain and 3/4/5 draft picks. Both spawns must reach every altar.
Every output passes the official map builder and game loader. Regeneration must match
the immutable manifest in `mechanics/generated-maps-g1.json`; different bytes are rejected.
Generated binaries are local build artifacts. The 11 `00*` site maps remain a separate
diagnostic set. The ten `01*` site maps join the generated confirmation set.
Confirmation maps have only been structurally validated; no confirmation games were run.

## Actor contract v1

An actor is `(episode, team, champion, round)`. Every champion has a separate policy
instance and private RAM. Only the official **8 shared bytes** can communicate live
team state; the 1,024 draft bytes are frozen after drafting. Python's ability to batch
all actors must never become an extra team communication channel.

Reset returns public terrain and the first actor observation. Observations use the
engine's authenticated team/champion perspective: own state and inventory, visible
champions/camps, native vision and movement masks, own ability metadata/cooldowns,
public gem banks and the team's shared bytes. Hidden health and enemy inventory are
excluded. A verification-only test mutates hidden enemy health and requires identical
actor observations; the privileged test module is never loaded by the worker.

`lab/policy.py` defines 24 clipped global features and 16 candidate rows of 12 features.
The stable proposal order is wait, ready self spells, up to four visible attacks, then
adjacent moves in row order. Padding is masked. Each row has an explicit action mapping.
This is a bounded micro-policy proposal set; macro decisions such as purchases, tribute,
recall and other spell types remain explicit controller actions. The environment also
supports those actions directly. Known attack-reset prerequisites are filtered; native
action results remain authoritative if new obstructions or other conditions reject a proposal.

An action returns its native error code, accepted/result flags, whether the turn ended,
and the next actor observation. There are at most **two decisions per champion turn**;
wait yields immediately. Re-encode after the first action before choosing the second.
This conservative cap follows the measured release fuel envelope.

Only phase-2 completion returns an outcome and final banks. A full tie is a team-B win.
Timeouts, failures and truncated rollouts have no win/draw/loss label. The native worker
does not execute submitted bot WASM or meter a Python policy's fuel: every exported bot
must still pass the official release runner and promotion gate.

## Release proof and supported model size

The representative candidate MLP has 24 global inputs, 12 candidate inputs, eight hidden
units and 16 candidate scores: **305 float32 parameters / 1,220 weight bytes** per actor.
The C++ kernel uses explicit four-lane WASM SIMD and separate multiply/add operations;
its float32 logits and masked argmax match the Python reference. Larger architectures,
new features or additional decision passes need a new fuel certificate.

The release probe runs two complete observation/encode/inference passes per active turn,
then a small scripted controller and compact binary logging. Four complete 2,000-round
matches cover 3/4/5-pick maps, both seats, linked Cassi/Issac bodies, movement, attack,
spells, purchases, recall and tribute. All 2,560 logged actor frames are checked for
features, candidate masks, movement masks, float32 scores and action-result parity.
The replay then continues to completion and compares the official winner, round and banks.
This is a bounded adapter regression suite; future engine patches and new action types
still require fresh coverage. It does not prove every possible game trajectory.

The admission limits are 65,000 fuel for two encode/inference passes and 85,000 for the
ordinary-turn controller before logging, with zero official faults or fuel exhaustion.
Observed maxima are recorded per map in `results/stage1-parity.json`. These are measured
envelopes, so retain fuel checks throughout training and export.

## Calibration and speed

The five frozen controls completed 2,500 release games on all 100 generated screening
maps: each ordered pair including mirrors, with zero faults or fuel exhaustion.
Starter rates 1,828, its alternate-seed twin 1,812, the 10% skip control 1,790, the 50%
skip control 1,384 and idle 687. The seed gap is 16 points, versus handicap gaps of
38 and 444. Starter and seed score 50% head to head over 200 games.
The small handicap's bootstrap intervals overlap; its lower point estimate passes the
predeclared ordering check, not a claim that every 38-point change is significant.
Always retain map-level uncertainty, both seats and controls in later comparisons.

`results/stage1-throughput.json` records a 16-environment benchmark with all actor
observations, JSON serialization and Python IPC. The separate native idle-tail rate
omits intermediate observations and cannot be used as a training throughput claim.
Both measurements are machine-specific; the readiness floor is 500 observed turns/s.
The earlier official five-bot calibration took about eight minutes with four workers.

## Reproduce

Install `requirements-lab.txt`, run `cambc init --yes .`, and install Node.js 22+.
If the pinned engine asset is absent, run `cambc mapeditor --no-browser` once and stop
the local server after it starts. Set `CAMBC_ENGINE_WASM` to the exact asset path if
automatic discovery does not find it. `CAMBC_NODE` and `CAMBC_CLI` can select executables.

```bash
python -m lab stage1 maps
python -m lab freeze bots/dummy dummy-week2-v1 --parent ""
python -m lab freeze bots/starter-cpp starter-week2-v1 --parent ""
python -m lab freeze bots/calib-seed calib-seed-week2-v1
python -m lab freeze bots/calib-skip10 calib-skip10-week2-v1
python -m lab freeze bots/calib-skip2 calib-skip2-week2-v1
python -m lab stage1 calibrate
python -m lab stage1 verify
python -m lab stage1 benchmark
python -m pytest -q tests
python -m lab stage1 ready
```

Skip a freeze command if that exact frozen version already exists. Archives are immutable.
All commands run from `next/`. Windows can pass a writable `--basetemp` to pytest.
The `ready` command fails when a source/configuration hash changes; regenerate the
relevant proofs before using it to admit Stage 2.

## Stage 2 handoff

Collect baseline demonstrations only after `ready` passes. Each record must retain the
engine/SDK/adapter/model schema, map hash, both frozen opponents and lineage, seat,
champion, round, decision index, authenticated observation, candidates/mask, chosen native
action and result. Track teacher actions missing from the proposal set explicitly;
never relabel an unsupported action as wait. Keep actor inputs separate from any
centralized critic state. Terminal labels belong only to completed games.

Split by whole match and map family/seed and opponent lineage, with both seats in the
same partition; adjacent turns must never leak across train/validation. Use screening
maps for development and a separately reserved screening subset for model validation.
Keep the 60 generated and ten site confirmation maps sealed for the promotion gate.
Stage 3 should report proposal coverage before imitation accuracy. No baseline replay
dataset or learned model is included in Stage 1's diagnostic traces.
