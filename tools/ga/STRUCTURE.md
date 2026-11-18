# Structure evolution of the micro (levels 1-3)

`ga.py` evolves the 22 thresholds of the fight code (the weights). The decisions themselves stay fixed: a list of
rules in a fixed order, each comparing one variable with one threshold. `sga.py` lets the genetic algorithm change
that structure at three levels of freedom, on the same machinery (one instrumented wasm, candidates are
byte-patched copies, fitness = margin over the control on the same games, shrunk mean over generations).

| level | what evolves | genotype | bot side |
|---|---|---|---|
| 1 | which micro rules run, their order, the existing fight switches | dict of int genes | `struct.patch`: play_turn's micro section as a rule list |
| 2 | the conditions "back off from this group" (GP0) and "engage this target" (GP1) | two expression trees | `ga_run`: postfix interpreter, ~1 fuel per token |
| 3 | a NEAT net choosing the action while enemies are in sight | NEAT genome (nodes, links, innovations) | `ga_nn_act`: ordered feed-forward net, <= 32 nodes, <= 128 links |

## Level 1: rules and their order

The micro of `bots/study27-economy` is this list (first rule that acts ends the turn):
FLEE (below the flee % hp), NEARRECALL, FM (off), KITE, FRONT, AVOIDLOW, AVOID, ENGAGE, RECALLSHOP, WALKHOME (off).
Healing on spawn stays first; banking gems, grouping and farming stay last (macro).

Genes (`structure.py SWITCHES`): an on/off gene per rule (`P_R_*`, or the existing `P_FRONT`, `P_KITE`,
`P_WALKHOME`), an order gene per rule (`P_O_*`, random keys: rules run sorted by them, ties keep the base order),
and the existing switches the fight code already has (`P_HITFIRST`, `P_SAFESTEP`, `P_RETREAT`, `P_NOCHASE`,
`P_FRONT_LOCAL`, `P_SHOOT`, `P_GANG`, `P_CALLHELP`, `P_TWIN`, `P_ALLYDUTY`, `P_CARRY`, `P_U34_ENGAGE_FALLBACK`).
The weights stay at `--base` unless `--evolve-weights`.

## Level 2: genetic programming of the two conditions

A program is a tree over 25 fight features (`structure.FEATURES`: hp %, nearest enemy, enemies and allies within
4 and 8, our hp vs theirs around us and around the target, favourable / killable / reachable, target hp % and
distance, gems carried, distance home, ready enemy damage on our tile, on spawn, target channelling, help call,
caster draft, round, hit this round, champions of each side near the target, ranged), with + - * min max < >
and or not if. It travels in the genome as postfix tokens (<= 47) and the bot runs it where the fixed
condition was. The seeds are the base bot's own conditions:

    GP0 = (not FAV and not KILL) and ((HP < 60 or not NEAR > 4) and not SPAWN)
    GP1 = (KILL or TCHAN) or ((REACH and FAV) or HELP)

Operators: threshold nudges, operator swaps, hoist, wrapping a node in `and`/`or` with a new comparison, fresh
subtrees, subtree crossover.

## Level 3: NEAT

Inputs: the same 25 features, scaled. Outputs: default (let the rules decide), engage, kite, back off, flee,
recall, farm; argmax. The seed net has no links and a bias of 1 on "default", so it is the base bot, and evolution
only has to find the situations where another action wins (adding links and nodes, NEAT speciation with an
adaptive threshold, the best of each species kept).

## Check that the default is the base

    python3 tools/ga/sga.py check --level 1|2|3      # unlimited fuel: control, seed and base build play identical games

16 Oct: 68/68 identical games for all three levels (17 site maps, both sides, vs study27-economy and spar11).

## Commands

```bash
python3 tools/ga/sga.py prepare                                    # once, ~15 s
nohup python3 tools/ga/sga.py run --level 1 --gens 40 > out/sga/L1/run.log &
python3 tools/ga/sga.py validate --level 1 --top 3                 # v100, sign test vs control
python3 tools/ga/sga.py export --level 1 --id ID --out out/sga/best1   # bot folder + best1.json
nohup python3 tools/ga/sga.py run --level 2 --base out/sga/best1.json > out/sga/L2/run.log &
nohup python3 tools/ga/sga.py run --level 3 --base out/sga/best1.json > out/sga/L3/run.log &
```

`--base` also takes the weight GA's best genomes by id (`9872f93cac`, `78880781f7`) or inline JSON. Each level has
its own state under `out/sga/L<n>/` (state.json, log.md, games.jsonl) and resumes from it.

Opponents by default: study27-economy (the online bot), spar11, spar16 and the weight GA's two best genomes
(`/mnt/project-files/analysis/ga-micro-2026-10-16/genomes/`), since the caster panel alone is saturated
(the online bot wins 67-8, 85-4, 65-9 against it on v100).

An exported genome is judged as a normal bot by `tools/gate.py` (fight kind: decided online).
