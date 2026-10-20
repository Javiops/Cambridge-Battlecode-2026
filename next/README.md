# next: a fresh start, built the CarsonBurke way

A separate, self-contained project. It uses nothing from the rest of this repo. If it works, we move to it.

The idea, from CarsonBurke's public bots and postmortems: **build the measuring loop before the bot**.
Every version is frozen and rated against every other, on fixed map sets, from both sides, with stats
that explain *why* a version wins or loses. Only then do we write the bot, one change at a time.

Start with [AUDIT.md](AUDIT.md) (this lab next to what Carson built), [AGENTS.md](AGENTS.md) (how we work), then [DECISIONS.md](DECISIONS.md) (what we know, with numbers)
and [ROADMAP.md](ROADMAP.md) (what is next).

**Stage 1 is complete for the October 20 patch.** See [STAGE1.md](STAGE1.md) for the
training interface, observation/action contract, release fuel certificate and reproduction
commands. `python -m lab stage1 ready` verifies the saved evidence against current hashes.
Stage 2's first baseline dataset is now collected and audited. See [STAGE2.md](STAGE2.md)
and `python -m lab stage2 ready`. Stage 3's first behavioural cloning model is trained,
exported and tested in release matches. See [STAGE3.md](STAGE3.md) and
`python -m lab stage3 ready`. It is a local actor warm start; the live bot is unchanged.
Stage 4's inventory-aware outcome critic passes its fresh prediction and pipeline gates: 24 release games on eight unseen maps, with both Brier and log loss better than the independently fitted score/time baseline. See [STAGE4.md](STAGE4.md) and `python -m lab stage4 ready`.
Stage 5's first PPO self-play run is trained and audited. Its native strength gate is **PASSED** (60.9% over 64 fresh paired games). See [STAGE5.md](STAGE5.md) and `python -m lab stage5 ready`.
Stage 6 integrates that unchanged actor and controller into C++/WASM. It passes
262,936 exact native decisions over 16 full release matches, with zero faults or
fuel losses and an exact source-bundle rebuild. See [STAGE6.md](STAGE6.md) and
`python -m lab stage6 ready`.
Stage 7's expert/PPO hybrid `ppo-league-v12` passes the unchanged promotion gate:
140/140 wins (100.00%) against starter on 70 fresh paired maps,
zero bot faults, fuel losses within the allowed limit, and an exact source rebuild.
See [STAGE7.md](STAGE7.md) and `python -m lab stage7 ready`. The matched actor-disabled
control also clears screening, so the strength gain is attributed to the strategic
controller. Neither confirmation pool is sealed any longer.

**Patch 1.0.1 release follow-up:** v12 is live as platform v83. Its source ZIP
matches the qualified artifact and server compilation succeeded. The initial
Nyx sparring group wins 1/5; a later paired top-ten scouting batch wins 4/120,
with zero bot faults and 29 fuel losses, all on `01big-world`.
See [HOTFIX-1.0.1.md](HOTFIX-1.0.1.md) for audited deployment and replay evidence.

**Current development:** [TOPDRAFT.md](TOPDRAFT.md) records a separate Fish-draft
fork and coordinated single-objective rallies. V3 stages five/six allied bodies
before assaults, improves elk-arena income, and still regresses on Stampede.
It remains offline. The hourly unranked loop now focuses primarily on nearby and
moderately stronger teams, with a small leader-scouting allocation.

## Setup

```bash
cd next
python3 -m venv .venv             # Python 3.12 recommended
source .venv/bin/activate
python3 -m pip install -r requirements-lab.txt
cambc init --yes .               # refresh the SDK and official toolchain
python3 -m pytest -q tests
python3 -m lab probe             # verify the actual release engine and regenerate mechanics
```

On Windows, create the environment with `py -3.12 -m venv .venv`, activate it with
`.venv\Scripts\Activate.ps1`, then use `python` wherever this file says `python3`.
The project environment pins CAMBC 3.0.1. See [PATCH-2026-10-20.md](PATCH-2026-10-20.md)
before migrating old frozen versions or interpreting pre-patch ratings.
The fast actor environment also requires Node.js 22+ and the pinned official map-editor
rules asset. Follow [the Stage 1 setup](STAGE1.md#reproduce), then generate the map pool with
`python -m lab stage1 maps` before running the default league.

## Run the league

```bash
python3 -m lab freeze bots/dummy dummy-week2-v1 --parent ""
python3 -m lab freeze bots/starter-cpp starter-week2-v1 --parent ""
python3 -m lab freeze bots/calib-seed calib-seed-week2-v1 --parent ""
python3 -m lab freeze bots/calib-skip10 calib-skip10-week2-v1
python3 -m lab freeze bots/calib-skip2 calib-skip2-week2-v1
python3 -m lab league --mirror                 # writes results/REPORT.md
python3 -m lab watch starter-week2-v1 dummy-week2-v1 00corners
python3 -m lab probe                           # regenerate mechanics/constants.md from the engine
python3 -m lab list                            # versions, parents, changelogs
```

After a candidate beats the references on screening maps, freeze it under a new name and run
`python3 -m lab gate CANDIDATE`. Use `python3 -m lab bundle CANDIDATE` only for the exact version
that passed. Confirm maps are reserved for this promotion check.

Every league writes `results/REPORT.md` and `results/dashboard.html` (open it in a browser).
To run Carson's ablation loop with Claude Code, use `/ablation` (see `ablations/ABLATION_PROMPT.md`).

Games are stored in `results/games/`. Cache keys include the ordered WASM hashes, map bytes,
CLI, SDK fingerprint, pinned engine build and parser version. Old frozen versions are preserved;
the current league requires fresh versions recorded against this runtime.

## What is here

| path | what |
|---|---|
| `lab.toml` | all settings: map sets, panel, champion, gate thresholds |
| `lab/` | the loop: `core.py` (freeze, play, store, watch, bundle), `stats.py`, `rating.py`, `report.py`, `gate.py`, `dashboard.py`, `probe.py` |
| `mechanics/` | engine facts printed by `bots/probe` |
| `ablations/` | the ablation overseer prompt |
| `tests/` | tests for the judge itself |
| `bots/dummy` | the floor: never acts |
| `bots/starter-cpp` | the SDK starter, the weak reference |
| `bots/calib-*` | calibration bots of known strength (same, -10% turns, -50% turns) |
| `bots/probe` | prints constants, all 13 champion bodies, all 6 camps, dash and CC designs |
| `bots/contract-probe` | release observation/action parity and SIMD inference fuel certificate |
| `lab/environment.py`, `lab/engine.mjs` | persistent batched actor access to the exact official rules module |
| `lab/mapgen.py`, `mechanics/generated-maps-g1.json` | deterministic generator and immutable map hashes |
| `results/stage1-*.json`, `STAGE1.md` | source-bound Stage 1 exit checks and Stage 2 handoff |
| `lab/dataset.py`, `lab/replay*.mjs`, `lab/replay.py` | native replay importer, split plan, demonstrations and audit |
| `STAGE2.md`, `results/stage2-*.json` | dataset contract, live sparring evidence and Stage 3 handoff |
| `results/calibration-2026-10-17.md` | the first league report |
| `maps/` | 100 generated screen maps; 60 generated + ten site confirm maps; 11 separate `00*` diagnostics |
