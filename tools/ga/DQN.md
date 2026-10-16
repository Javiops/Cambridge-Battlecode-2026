# Deep Q-learning and a learned fight value for the micro

`dqn.py` and `fightval.py` add learned decision makers to the fight micro, on the same machinery as the genetic
algorithm (one instrumented wasm, candidates are byte-patched copies, judged against the control on the same games).
Results and the plain-language assessment: `/mnt/project-files/analysis/dqn-2026-10-16/README.md`.

## Where the net acts

The structure GA (`struct.patch`, `ga_struct.h`) turned the micro into a rule list and gave the level-3 NEAT net a
hook: while enemies are in sight and we are off our spawn, a net reads the 25 fight features (`GaFeat`: hp %,
nearest enemy, enemies/allies within 4 and 8, hp ratio, target hp and distance, gems, distance home, ...) and picks
one of 7 actions: 0 let the rules decide, 1 engage, 2 kite, 3 back off, 4 flee, 5 recall, 6 farm.
`dqn.patch` + `dqn.h` put a dense **25-32-7 Q-network** on that hook (about 1,000 multiplies per decision; the
2026-10-15 fuel probe measured ~2.5 fuel per multiply with SIMD, so a few thousand fuel of the 100k turn).
Weights live in `volatile int dq_g[]` (magic `DQN1`, x4096), copied into floats once per champion.
All-zero weights = Q equal for every action = action 0 = the control: 136/136 identical games with unlimited fuel.

Header fields (`dq_ints`): mode (0 off, 1 Q argmax, 2/3 death value: back off / flee when p(die) > margin per mille),
epsilon per mille (random valid action, data collection only), log, seed, hidden units, margin (an action must beat
Q(default) by margin/1000 gem-equivalents).

## Pipeline

1. **Log** (`collect`): games with epsilon-greedy around the rules (or around a trained net); each decision prints
   `[dq] NAME round action greedy valid f0..f24` and each turn of a contact `[dt] NAME round alive hp maxhp gems gold`
   (flushed at once: unflushed output is lost at the end of a turn). `extract_logs` reads `team-a/b.stdout` from the
   replay bundle. ~250 decisions per game per team; 1,500 games = ~370k transitions in 10 min on 4 cores.
2. **Reward** (`transitions`), gem equivalents per decision, until the next decision of the same contact:
   +gems picked up (banked gems are neutral), +10 x hp change as a fraction of max hp, +0.1 x gold earned (kills,
   assists), death = -(25 + the bag) and the episode ends. A contact ends 15 rounds after the last decision
   (terminal, bootstrap 0). gamma = 0.9 per decision.
3. **Train** (`train`): offline double DQN (fitted Q iteration with a target net), Huber loss, action-rarity weights,
   a CQL-style conservative term; `--onestep` evaluates the logged policy instead (SARSA) and acts greedily.
   numpy only, ~20 s on 350k transitions. Held-out TD error is printed as a sanity check, not as a verdict.
4. **Embed and judge** (`eval`): candidate (eps 0, log off) and control (mode 0) in the same template on v100
   (100 maps never trained on), both sides, vs ga65a6 (v44), study27-economy, spar11, spar16. Score = map-rival
   pairs where the candidate's two-sides result beats the control's, sign test. Then `tools/gate.py` as usual.
5. **Export** (`export --migrate /mnt/project-files/ga-farm/migrants`): bot folder + `dqn_<id>.json/.wasm`.

## Learned fight value and behaviour cloning (`fightval.py`)

Same features computed from the decoded every-round replays of the #1/#2 teams (101 games, 68k contact turns) and
from our own collection logs (373k decisions). Labels: dies within 10 rounds; next-round step vs the nearest enemy
(approach / hold / retreat). Only features a replay can show are used (no target choice, spell timers or chat).
The models export into the same `dq_g` slot: mode 2/3 (risk threshold) or mode 1 (cloned moves).

## Commands

```bash
python3 tools/ga/dqn.py prepare
python3 tools/ga/dqn.py collect --games 1500 --eps 300
python3 tools/ga/dqn.py train --out out/dqn/net1.json
python3 tools/ga/dqn.py eval --net out/dqn/net1.json --margin 3000
python3 tools/ga/fightval.py data --steps out/top2/steps --dqn out/dqn/data
python3 tools/ga/fightval.py fit --src ours --label die10 --greedy-only --out out/fightval/die_ours_g.json
python3 tools/ga/fightval.py compare
python3 tools/ga/dqn.py --work out/dqn2 eval --net out/fightval/die_ours_g.json --mode 2 --margin 300
```

Note: a change to `dqn.h` needs a new `prepare` in a new `--work` folder (the game cache is keyed by genome, not by
template).
