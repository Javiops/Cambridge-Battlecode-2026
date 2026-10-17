# next: a fresh start, built the CarsonBurke way

A separate, self-contained project. It uses nothing from the rest of this repo. If it works, we move to it.

The idea, from CarsonBurke's public bots and postmortems: **build the measuring loop before the bot**.
Every version is frozen and rated against every other, on fixed map sets, from both sides, with stats
that explain *why* a version wins or loses. Only then do we write the bot, one change at a time.

Start with [AUDIT.md](AUDIT.md) (this lab next to what Carson built), [AGENTS.md](AGENTS.md) (how we work), then [DECISIONS.md](DECISIONS.md) (what we know, with numbers)
and [ROADMAP.md](ROADMAP.md) (what is next).

## Setup

```bash
pip install cambc pytest          # the official CLI (2.2.5) and the test runner
cd next
cambc init --yes .                # SDK and toolchain; the maps are already in maps/
python3 -m pytest -q tests        # the lab's own tests
```

On Windows (the PC copy in `C:\Users\Javier\Cambc2026\next`): run `.venv\Scripts\Activate.ps1` first, then type `python` wherever this file says `python3`. The venv holds cambc 2.2.5; the PC-wide cambc (2.2.1) is left alone for the old project.

## Run the league

```bash
python3 -m lab freeze bots/dummy dummy-v1
python3 -m lab freeze bots/starter-cpp starter-v1
python3 -m lab league --mirror                 # writes results/REPORT.md
python3 -m lab gate starter-v1                 # promotion gate on the confirm maps
python3 -m lab watch starter-v1 dummy-v1 corners   # rerun one game with logs and open the viewer
python3 -m lab bundle starter-v1               # upload zip, proven to rebuild the gated bytes
python3 -m lab probe                           # regenerate mechanics/constants.md from the engine
python3 -m lab list                            # versions, parents, changelogs
```

Every league writes `results/REPORT.md` and `results/dashboard.html` (open it in a browser).
To run Carson's ablation loop with Claude Code, use `/ablation` (see `ablations/ABLATION_PROMPT.md`).

A full league of 5 versions on 12 maps is 300 games and takes about 100 s on 4 cores. Games are stored in
`results/games/` and never replayed (the engine is deterministic).

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
| `bots/probe` | prints engine constants and champion stats |
| `results/calibration-2026-10-17.md` | the first league report |
| `maps/` | the 17 site maps, pinned so results stay comparable |
