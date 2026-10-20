# next: a fresh start, built the CarsonBurke way

A separate, self-contained project. It uses nothing from the rest of this repo. If it works, we move to it.

The idea, from CarsonBurke's public bots and postmortems: **build the measuring loop before the bot**.
Every version is frozen and rated against every other, on fixed map sets, from both sides, with stats
that explain *why* a version wins or loses. Only then do we write the bot, one change at a time.

Start with [AUDIT.md](AUDIT.md) (this lab next to what Carson built), [AGENTS.md](AGENTS.md) (how we work), then [DECISIONS.md](DECISIONS.md) (what we know, with numbers)
and [ROADMAP.md](ROADMAP.md) (what is next).

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

## Run the league

```bash
python3 -m lab freeze bots/dummy dummy-week2-v1 --parent ""
python3 -m lab freeze bots/starter-cpp starter-week2-v1 --parent ""
python3 -m lab freeze bots/calib-seed calib-seed-week2-v1 --parent ""
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
| `results/calibration-2026-10-17.md` | the first league report |
| `maps/` | current 21-map pool (`00*` screen, `01*` confirm); old maps remain historical |
