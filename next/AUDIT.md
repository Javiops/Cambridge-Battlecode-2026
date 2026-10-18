# Audit: this lab against what CarsonBurke actually built

Sources read: cb-bc (Battlecode 2025, top 3: `AGENTS.md`, `elo.py`, the stats wrapper, the React dashboard,
`ABLATION_PROMPT.md`), kaggriculture (Kaggle, about 10th of 10,246), orbit-wars, The International, screeps-rl.
Status: **same** = what he did, **adapted** = his idea changed to fit CAMBC or a local PC, **gap** = not done yet.

## The measuring loop

| Carson | ours | status |
|---|---|---|
| Every version kept as a folder, never edited after (`bots/v1`, `v2` ...) | `lab freeze` copies source and `bot.wasm` into `archive/NAME`, refuses to overwrite | same |
| Lineage: the new bot is named after its parent; changelog is the first comment of the file | `meta.json` holds `parent` and the changelog line; the report draws the tree | same |
| Round robin, every pair, both sides of every map | `lab league`: every pair, both sides, every screen map; `--mirror` adds self-play | same |
| TrueSkill ratings in `elo.py` | Bradley-Terry fit on the Elo scale (TrueSkill would not install), plus a 90% bootstrap over maps | adapted |
| 300 s timeout per game | `TIMEOUT = 300` in `core.py`; a hung game is reported, not waited on | same |
| Win matrix and economy stats per bot | Win matrix, gems at round 500, round reaching 1000, deaths, kills, gold, camps, wards, fuel lost | same |
| Stats snapshot every 100 rounds | `stats.py` samples the engine's timelines every 100 rounds | same |
| Rating progression and biggest jump in `history.json` | `results/history.jsonl` and a "Best rating per league run" table | same |
| Stop when the best gains less than 20 points twice | `plateau_points = 20`, printed as **Plateau** in the report | same |
| React dashboard | `results/dashboard.html`: one self-contained file with the gem curve and the rating per run | adapted (no server needed on the PC) |
| Replays to watch losses | `lab watch A B MAP` reruns that exact game with logs and opens `cambc view` | same |
| Games run in parallel | one game per CPU core; finished games are cached by bot bytes + map + CLI version | adapted, and cheaper: an unchanged pairing is never replayed |

## Judging a change

| Carson | ours | status |
|---|---|---|
| kaggriculture finalist gate: ≥ 0.5 vs the best bot, ≥ 0.9 vs starter | `lab gate`: ≥ 50% vs champion, ≥ 90% vs starter, 0 faults, fuel limit | same |
| Gate on seeds the bot was never tuned on | screen maps (12) for work, confirm maps (5) only for the gate | adapted; only 17 maps exist, so this is weak until the map generator |
| Frozen versioned validation panel (orbit-wars) | `panel` + `panel_version` in `lab.toml`; reports from different panels are never mixed | same |
| Symmetry and seat tests (orbit-wars) | seat split per version and mirror side-A share in every report | same |
| Frozen bytes are what gets uploaded | `lab bundle` zips, rebuilds the zip, checks the sha256 matches the gated `bot.wasm` | same |
| Configs are the source of truth | every number lives in `lab.toml` | same |
| Know the noise before trusting a gain | calibration bots of known strength; the noise pair's gap is printed in every report (about 60 points) | added: our own A/B history shows we need it |
| Win/draw/loss beats shaped proxies (kaggriculture lesson) | the rating uses only the result; stats explain, they never decide | same |

## How the bot gets built

| Carson | ours | status |
|---|---|---|
| `AGENTS.md` written on day 1 | `AGENTS.md` | same |
| `mechanics/` notes of engine facts | `mechanics/constants.md`, printed by `bots/probe` inside a real game (`lab probe`) | same, regenerated rather than typed |
| `DECISIONS.md` with the reason for each choice (screeps-rl) | `DECISIONS.md` | same |
| LLM Ablation Overseer: parallel agents, one hypothesis each, shared best baseline | `ablations/ABLATION_PROMPT.md` and `/ablation` command | same; not used yet because there is no real bot yet |
| Correctness before optimisation (screeps-rl) | `tests/` check the judge itself (stats, ratings, snapshot rounds) | same |
| Data-oriented layout: Utils, Procs, Services, Data, Tasks (The International) | nothing yet: the bot is still the starter | gap, for the bot phase |

## What is still missing

| Carson | why it matters here | plan |
|---|---|---|
| Unseen seeds for the gate | qualifying maps are new; 5 site maps cannot tell "general" from "lucky" | map generator (ROADMAP 1) |
| Opponents he did not write (best public bots, held-out references) | a bot that only beats its own family can still lose online | ghosts of top-team play rebuilt inside `next/` once the bot can play |
| Hardness selector (kaggriculture league) | spend games on the opponents we are close to, not on the dummy | add after there are 5+ real versions |
| Ranking by a conservative rating (mean minus spread) | stops a lucky version topping the table | easy; add when two versions are close |
| Strategy collapse check | he saw his bot always bought the same thing too late | "Strategy coverage" table already in the report; watch it |
| Remote test runs | he ran on the real server; we can only run unranked games by hand | local `--release` runs enforce fuel, which was his main reason |

## What our old approach did that he never did

Many switches tested at once on one shared base, judged by one panel run, with no noise band, no frozen bytes
and no record of why. That is how 10/16 and 10/17 were spent. The lab makes each of those impossible by default.
