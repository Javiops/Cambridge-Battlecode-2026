# Genetic algorithm for the fight parameters (idea I030)

Evolves the bot's **micro** (when to fight, back off, flee, recall, chase, kite) while the **macro** (draft, shop,
camp choice, tributes) stays exactly as the base bot has it. The base is `bots/study27-economy`, the bot active
online since 16 Oct (copied from `fran/study27-economy`; `main` gets it with PR #17).

## Genome

22 integer genes, listed with their default, range and meaning in `genome.py`:
17 existing `P_*` macros of the fight code (flee and recall thresholds, engage ratio, front line, kite, volley,
chase, danger spots) and 5 literal constants of the fight code turned into genes (`P_GA_*`: back-off hp, engage
ratio without a target, "killable" factor, kite give-up ratio, spawn heal level). The default genome equals the base.

## Why it is fast

`prepare` compiles one instrumented copy of the base whose genome lives in a `volatile int` array marked by a magic
number. A candidate is that wasm with the genome bytes patched: no compile per candidate.

Instrumenting changes fuel use slightly, and this bot is fuel-chaotic: the default genome plays 111 of 136 games
exactly like the base and 25 differently; with unlimited fuel (`cambc run --fuel 10000000`) the games are
identical. So the GA's reference is always the **control** (default genome, same instrumented wasm) on the same
games, never the base build, and an exported winner is judged again as a normal build by `tools/gate.py`.

## Fitness and selection

Per generation: 12 maps drawn fresh from the training pool (official 17, maps_gen, arena gen2/gen3/f150, minus
anything identical to a sealed or validation map), every candidate plays them from both sides against 4
opponents: the base itself and the caster panel spar11, spar12, spar16 (the one local rival that kills like online
teams). Pair score = (side A + side B) / 2 with win +1, loss -1, plus 0.1 x gem margin / 1000; fitness = mean
over pairs, averaged over opponents.

Selection uses the margin over the control on the same games, averaged over all generations a genome was played
and shrunk toward 0 (`sum / (n + 1)`), so one lucky generation does not win. 4 elites are kept and re-played on new
maps every generation; the rest are children (tournament of 3, blend crossover, gaussian mutation of ~3 genes).

Cost: 16 genomes x 4 opponents x 12 maps x 2 sides = 1536 games, about 7-8 minutes on 4 cores.

## Map sets

| set | use |
|---|---|
| training pool (211 maps) | a fresh sample of 12 per generation |
| `arena/maps/v100` | `validate`: the top genomes vs the control, maps never trained on |
| `maps_hold60`, `maps_dev200`, `fresh300` | sealed: only `tools/gate.py` on the exported bot |

## Commands

```bash
python3 tools/ga/ga.py prepare --base bots/study27-economy
python3 tools/ga/ga.py check                       # default genome vs base (expect only fuel-chaos differences)
nohup python3 tools/ga/ga.py run --gens 300 --pop 16 --maps 12 > out/ga/run.log &   # resumes from out/ga/state.json
python3 tools/ga/ga.py validate --top 3            # v100, all opponents, sign test vs control
python3 tools/ga/ga.py export --id <genome id> --out bots/<name>
python3 tools/gate.py bots/<name> bots/study27-economy --kind fight --idea I030
```

Progress: `out/ga/log.md` (one line per generation), `out/ga/state.json`, games cache `out/ga/games.jsonl`.

## Phase 2 (only if phase 1 shows headroom)

Replace the fixed back-off thresholds with a tiny policy evaluated once per turn: a logistic unit or one hidden
layer of ~8 over ~15 inputs (our hp %, foes and allies within 4/8, their hp vs ours, ready enemy spells, gems
carried, distance to spawn). Its weights become genes of the same GA (neuroevolution). Measured cost of a net that
size is well under 1k fuel of the 100k per turn (thread "Is RL viable", fuel probe).
