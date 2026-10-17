# next: a fresh start, built the CarsonBurke way

A separate, self-contained project. It uses nothing from the rest of this repo. If it works, we move to it.

The idea, from CarsonBurke's public bots and postmortems: **build the measuring loop before the bot**.
Every version is frozen and rated against every other, on fixed map sets, from both sides, with stats
that explain *why* a version wins or loses. Only then do we write the bot, one change at a time.

Start with [AGENTS.md](AGENTS.md) (how we work), then [DECISIONS.md](DECISIONS.md) (what we know, with numbers)
and [ROADMAP.md](ROADMAP.md) (what is next).

## Setup

```bash
pip install cambc pytest          # the official CLI (2.2.5) and the test runner
cd next
cambc init --yes .                # SDK and toolchain; the maps are already in maps/
python3 -m pytest -q tests        # the lab's own tests
```

## Run the league

```bash
python3 -m lab freeze bots/dummy dummy-v1
python3 -m lab freeze bots/starter-cpp starter-v1
python3 -m lab league --mirror                 # writes results/REPORT.md
python3 -m lab gate starter-v1                 # promotion gate on the confirm maps
```

A full league of 5 versions on 12 maps is 300 games and takes about 100 s on 4 cores. Games are stored in
`results/games/` and never replayed (the engine is deterministic).

## What is here

| path | what |
|---|---|
| `lab.toml` | all settings: map sets, panel, champion, gate thresholds |
| `lab/` | the loop: `core.py` (freeze, play, store), `stats.py` (per-game record), `rating.py`, `report.py`, `gate.py` |
| `tests/` | tests for the judge itself |
| `bots/dummy` | the floor: never acts |
| `bots/starter-cpp` | the SDK starter, the weak reference |
| `bots/calib-*` | calibration bots of known strength (same, -10% turns, -50% turns) |
| `results/calibration-2026-10-17.md` | the first league report |
| `maps/` | the 17 site maps, pinned so results stay comparable |
