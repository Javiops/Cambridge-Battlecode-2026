# I019-I022 switches on study27-economy (the online bot), for teammates to test

Every switch defaults to 0, so with nothing defined this bot plays like the online one: 60 of 61 official + gen maps are
identical games, and the one that differs is the known fuel noise of any code change (0 won / 1 lost on both sides).
Full results and data on study28: [I019-I022-review-fixes.md](I019-I022-review-fixes.md) (in PR #16).

| switch | idea | status so far | try it |
|---|---|---|---|
| `P_ALTARPICK 1` (+ `_EN 12`, `_AL 3`, `_HOME 25`) | I019: the altar's cost adds 12 tiles per visible foe within 5, takes off 3 per ally within 4 (at most 2) and adds 25% of its walk home. Added on top of this bot's walking-distance banking (`br_altar_penalty`) | rejected on study28: 86-103 on 710 maps; not measured here | `tools/variante.sh t_alt study27-economy "#define P_ALTARPICK 1"` |
| `P_RECALLCOST 2` | I020: a shop trip needs `P_SHOP_RECALL + 2 x walk home` gold | **null here**: levels 1/2/3 = 123-130, 131-132, 132-129 on 1000 fresh maps (this bot's `cr_` policy already checks the walk home on capture-tile recalls) | `"#define P_RECALLCOST 2"` |
| `P_LOGRECALL 1` | I020: log the reason for every recall, plus the gold spent at home | logger only, use with `--keep`; script `analysis/four-fixes/recalllog.py` (PR #16) | `"#define P_LOGRECALL 1"` |
| `P_LOGCAMP 1` | I021: log predicted vs actual damage of every camp fight | logger only; script `analysis/four-fixes/camplog.py` (PR #16) | `"#define P_LOGCAMP 1"` |
| `P_CAMPMODEL 1/2/3` (+ `P_CAMPRESERVE`) | I021: the front champion takes the camp's whole strength (n, not n²); 2 = only at the camp; 3 = old model at the camp, reserve `P_CAMPRESERVE` | rejected on study28: 4-21, 15-36, 10-25 (5-13% slower farming) | `"#define P_CAMPMODEL 1\n#define P_CAMPRESERVE 0"` |
| `P_CHAINWALK 1/2` | I022: the camp before banking is picked by walking distance, like the altar here (`br_altar_distance`); 2 = by the bag's delay (walk + clear + capture + camp-to-altar) | rejected on study28: 19-23, 24-38. This bot is where the mixed metrics actually were, so it is worth re-measuring here | `"#define P_CHAINWALK 1"` |

How to measure one (from the repo root, after `cambc init --yes`):

```bash
tools/variante.sh t_chain study27-economy "#define P_CHAINWALK 1"
python3 tools/gate.py bots/t_chain main --kind farm     # or: python3 tools/ab.py bots/t_chain bots/study27-economy --sets dev,hold
```

Score by maps won on both sides. A result needs p<0.05 (about 150+ decided maps for a small effect), and before anyone
uploads it, an idea goes through the board (`python3 tools/idea.py set I0xx ...`).
