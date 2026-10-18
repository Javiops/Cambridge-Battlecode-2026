# Cambridge Battlecode 2026 (CAMBC 2026a)

C++ bots for [CAMBC 2026a](https://2026a.battlecode.co.uk).

**New foundation: start with the [short human guide](bots/foundation/README.md).**
Coding assistants: read [AGENTS.md](AGENTS.md); Claude also has [CLAUDE.md](CLAUDE.md).
The foundation currently holds position. Keep using the existing competition bot.

Strategies live in the English [tactics handbook](docs/tactics/README.md):
12 chapters and 96 decision topics. Write an idea there before implementing it.

## Team workflow

Ideas move through development and the local gate (`tools/gate.py`), paired online
A/B evaluation (`online/lfl.py`), and analysis (`online/dissect.py`). See the
[harness guide](harness/README.md) for the complete process and the
[idea board](harness/IDEAS.md) for status (`python3 tools/idea.py board`).

## Repository map

| Path | Purpose |
| --- | --- |
| `bots/foundation/` | New action contracts, SDK adapter and reproducible checks |
| `docs/tactics/` | Shared strategy specifications with stable topic IDs |
| `bots/v30/src/` | Historical v30 bot: draft, farming, combat and parameter switches |
| `bots/spar11`, `spar12`, `spar16` | Training opponents with ranged drafts; spar12 groups up, spar16 prioritizes ranged targets |
| `tools/arena.py` | Parallel games and summaries of wins, gems, deaths and kills |
| `tools/variante.sh` | Copy a bot, change `params.h` switches and compile it |
| `tools/ab.py` | Compile and compare a variant against a baseline on both sides of each map |
| `tools/gate.py` | Safety checks, fresh maps, ranged opponents and counterexamples; change-specific pass/fail verdict |
| `tools/idea.py` | Manage `harness/ideas/` and `harness/IDEAS.md` |
| `online/` | Challenges, results, paired version comparisons and analysis |
| `maps_gen/` | 44 generated training maps; heavily tuned against, so unsuitable for final decisions |
| `maps_hold60/` | 60 sealed holdout maps, seed 20261015; final evaluation only, never tune against them |
| `maps_dev200/` | 200 development maps, seed 4242, for larger comparisons |

## Historical bot workflow

The commands below describe the existing v30 workflow. The previous README called
v30 the live version and reported rank 25 with v29; those are historical claims,
not a verified statement of the current upload. The foundation's
[source manifest](bots/foundation/baseline.json) records the baseline uncertainty.

```sh
pip install cambc==2.2.5
git clone https://github.com/Javiops/Cambridge-Battlecode-2026.git
cd Cambridge-Battlecode-2026
cambc init --yes
cambc build bots/v30
cambc run bots/v30 bots/spar11 --map maps/corners.map26a -o out/example
cambc view out/example
```

Create a separate variant; keep the baseline unchanged:

```sh
tools/variante.sh trial1 v30 "#define P_FINISH 40"
python3 tools/ab.py bots/trial1 bots/v30
python3 tools/ab.py bots/trial1 bots/v30 --sets official,gen,hold,dev
python3 tools/arena.py bots/trial1 bots/spar11 --maps "maps/*.map26a" --sides both --jobs 4 --out out/trial1_s11
```

Count maps, not games: a map win requires winning on both sides. `same game`
counts maps where the variant behaved exactly like the baseline and only the
side decided the outcome. The A/B tool bases its verdict on fresh maps and
reports the additional sample needed when results are inconclusive. Deterministic
games are cached in `out/ab-cache/`.

Use generated maps as well as official maps. Small changes can swing individual
results; require a clear difference across many maps. Local wins do not guarantee
online wins, so include the training opponents and the harness gates.

## Historical v30 behavior

- Map-based draft (`P_DRAFTUNI 2`): paths between bases of at most 45 tiles select
  ranged teams (3: Cassi&Issac, Ren, Stellar; 4: add Tavi; 5: Ryth, Stellar, Prism,
  Ren, Tavi). Longer maps select Vendetta, Varg, Cassi&Issac, Ryth, Tavi for farming.
- Ranged combat (`P_KITE`, `P_SWEEP 3`): cast at range four and keep distance.
- Retreat (`P_UNI_FLEE 35`, `P_RECALL_NEAR 5`): retreat below 35% HP; recall when
  the nearest enemy is at least five tiles away. Damage interrupts recall.
- Finish (`P_FINISH 30`, introduced in v30): pursue an enemy within six tiles
  when its HP is below 30%, even when it retreats.
- Shopping (`P_SHOPUNI 1`): Ren, Prism and Stellar buy power and some health.
- Switch defaults are near the start of `main.cpp` (`#ifndef P_...`); most have
  comments. Undefined switches generally default to zero unless set in `params.h`.

## Competition uploads

The existing upload process uses the team account: `cambc login`, then
`cambc submit bots/NAME`; activation happens on the competition website.
Upload and activation require an explicit team decision. Never commit login
tokens (stored outside the repository in `~/.config/cambc`).
