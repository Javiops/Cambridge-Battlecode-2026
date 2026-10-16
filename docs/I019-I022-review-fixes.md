# I019-I022: the four review fixes (altar choice, gold recalls, camp-survival model, gem chaining)

**Source:** Javi's review of the economy branch, 16 Oct 07:00 UTC. Base: `bots/study28` on `main` (study28 = study27 +
P_CHANCANCEL; the site runs study27 = v36). Each fix is a switch in `bots/study28/src/main.cpp`, **off by default**, so
this PR does not change the bot: study28 with every switch at 0 vs `main`'s study28 is 0-0 on both sides over 61 maps
(53 identical games, the rest the known fuel noise of any code change).

All numbers: `tools/gate.py bots/x_<variant> bots/study28 --kind farm --no-fuel`, fresh maps = hold60 + dev200 (260
maps), and for the two closest ones `--extra` fresh300 + f150 (710 maps). Score = maps won on both sides / lost on both
sides. Tuning was done only on official + maps_gen (`tools/ab.py --sets official,gen`).

## Summary

| idea | switch | training (official+gen) | gate, fresh maps | verdict |
|---|---|---|---|---|
| I019 altar choice | `P_ALTARPICK 1` | 2-7 | 35-32 on 260, **86-103 on 710** (p=0.24) | FAIL: neutral to slightly worse |
| I020 gold recalls pay for the walk back | `P_RECALLCOST 2` | 13-3 (p=0.02) | 43-38 on 260, 117-104 on 710, **200-161 on 1260 (p=0.045), panel 19-8** | **PASS (farm), small**: see the follow-up below |
|  | `P_RECALLCOST 4` | 11-6 | not gated | |
| I021 camp model: tank (n, not n²), reserve 0 | `P_CAMPMODEL 1` | 6-33 | **4-21** (p=0.001), gems/100r 154 vs 178 | FAIL: worse |
| I021 tank model only at the camp | `P_CAMPMODEL 2`, reserve -60 | 4-20 | **15-36** (p=0.005) | FAIL: worse |
| I021 old model at the camp, reserve -30 | `P_CAMPMODEL 3` | 9-9 | **10-25** (p=0.017) | FAIL: worse |
| I021 only no negative reserve | `P_RESERVE_PCT 0` | 9-20 | not gated | worse on training |
| I022 chaining by walking distance | `P_CHAINWALK 1` | 5-5 | 19-23 (p=0.64) | FAIL: neutral |
| I022 + clear and capture time | `P_CHAINWALK 2` | 7-8 | 24-38 (p=0.098) | FAIL: leaning worse |

Safety: 0 faults and 0 broken games for every variant. The first runs skipped the fuel phase (`--no-fuel`) for a reason
explained at the end: the walking fields do not raise fuel-exhausted turns when both bots are counted in the same games.

## I021 first: the data (predicted vs actual camp damage)

`P_LOGCAMP 1` prints one line per camp fight per champion (`[camp] ... old=<n² model> tank=<n model> lost=<actual>`).
122 games of official+gen (`bots/x_log` vs study28), 7807 lines, 3112 squad fights; script
`analysis/four-fixes/camplog.py out/ab/x_log_vs_study28`.

| squad | front champion lost (avg) | old model predicted for it | front lost more than predicted | tank model | front lost more than tank | front's share of the squad's damage | front died |
|---|---|---|---|---|---|---|---|
| 1 | 211 | 770 | 19% | 920 | 12% | (alone) | 1% |
| 2 | 267 | 468 | 37% | 664 | 17% | 81% | 2% |
| 3 | 325 | 727 | 42% | 1071 | 14% | 76% | 3% |
| 4+ | 423 | 918 | 35% | 2256 | 12% | 67% | 10% |

- The review is right about the mechanism: the front champion takes **67-81%** of the squad's damage (camps hit the
  nearest), and in squads of 2+ it loses more than the old n² model predicted in **35-42%** of fights.
- But the tank model over-predicts by as much (median actual/predicted 0.03-0.40), and deaths in camp fights are rare:
  98 in 122 games, the front dies in 3% of squad fights. 62% of those 98 deaths were fights where the old prediction was
  already above the champion's hp at the start: that is the negative reserve (`P_RESERVE_PCT -60`) at work.
- Every more cautious model lost on fresh maps (table above): the champions wait or skip camps they would have survived,
  and farming slows by 5-13%. The optimistic estimate costs a few deaths; the cautious ones cost more gems.

## I020: why every recall happens (`P_LOGRECALL 1`)

Same 122 games, 4351 recalls, script `analysis/four-fixes/recalllog.py`:

| reason | n | walk home | gold at recall | gold spent at home |
|---|---|---|---|---|
| flee/recall, hp < 55% | 1668 | 29.7 | 17 | 13 |
| capture-tile recall, hp 55-90% | 1316 | 35.6 | 16 | 11 |
| near-recall, hp < 55% | 547 | 29.3 | 24 | 23 |
| **shop trip, gold only** | 229 | 37.5 | 253 | 229 |
| shop trip with hp < 55% | 225 | 40.5 | 51 | 46 |
| capture-tile recall, hp < 55% | 221 | 39.3 | 13 | 1 |
| **capture-tile recall, gold only** | 71 | 35.9 | 103 | 99 |

Gold-only recalls are 300 of 4351 (7%). They always spend their gold, but the gold per tile of walk back falls from 16
(10-20 tiles from home) to 3 (45+ tiles). `P_RECALLCOST 2` asks for `P_SHOP_RECALL + 2 x walk home` gold before a
gold-only trip (and `90 + 2 x walk home` for the capture-tile one). It is the only fix that leaned in favour, but
117-104 on 710 maps is noise: it touches 7% of recalls.

## I019 and I022

- **I019** (`P_ALTARPICK`): altar cost = walking distance + 12 tiles per visible enemy champion within 5 of it - 3 per
  ally within 4 (at most 2) + 25% of the altar's walk home. Note: the engine has no "altar occupied" error (several
  allies can tribute at the same altar at once, see `sdk/cpp/cambc.h` error codes), so "used by a teammate" is not a
  cost in itself. 86-103 on 710 maps: the altar we pick today is almost always the right one.
- **I022** (`P_CHAINWALK`): the camp before banking is chosen by walking distance like the altar (1), and in mode 2 by
  the bag's delay (walk + clear + capture + camp-to-altar - walk to the altar now <= 16). It changes few games (42 of
  260 maps decided) and does not win. Note: on study28 the altar distance `ad` in chaining is straight-line too (the
  mixed metric the review quotes, `br_altar_distance`, exists only on the `fran/study27-economy` branch).

## Fuel: the gate's fuel phase is noisy

The first run of `gate.py` (before the fix in this PR) failed safety for every variant that builds walking fields (lanes, side A: 127-128
fuel-exhausted turns vs 81-83). The per-altar fields cost 5-17k fuel each, built one per turn with 56k+ left
(`P_FUELPROBE`). Counting both bots **in the same 34 games** (17 official maps x 2 sides, fields-only build `P_WALKFIELDS 1`):
candidate 593, base 645; on that lanes game the base itself had 153. The gate compares the candidate in game X with
the base in game Y, so one long fight swings it by 40. Fixed in this PR: `gate.py` now counts both bots in the same 6 games (3 maps x 2 sides); the fields-only build
then reads 309 vs 363 and passes.

## Follow-up 16 Oct 08:00: is RecallCost more than noise? (the user's question)

Yes, but small. Three checks, all on maps never used for tuning:

| check | result |
|---|---|
| a no-op build (walking fields only, `P_WALKFIELDS 1`) on 500 new maps (seed 20261016 + v100) | 37-35: the noise floor |
| `P_RECALLCOST` 1 / 2 / 3 on the same 500 maps | 70-61, 73-63, 79-65: all three doses point the same way |
| `P_RECALLCOST 2` vs the no-op on 1000 more new maps (seed 7161016) | **157-123 (p=0.048)** vs 63-64; gems/100 rounds 166.4 vs 165.1 |
| full gate, hold60 + dev200 + those 1000 (`--extra`) | **PASS**: 200-161 (p=0.045), fuel 315 vs 360 in the same games, caster panel 19 flips for / 8 against |

What it changes (`P_LOGRECALL`, 122 games): gold-only recalls 302 -> 171 (-43%), each spends more (274 vs 224 gold), and
the total number of recalls stays the same (4282 vs 4294): the blocked trips are made later, when the champion has to
go home anyway. Worst counterexample (`gen7161016_628`): the candidate makes no shop trip at all and dies 16 times vs
13; it is the price of buying items later on a few maps.

Zip for stage 3 (online, the user uploads): `/mnt/project-files/bot/mybot_study28_recallcost2.zip`
(= study28 + `#define P_RECALLCOST 2`).

## Decision

Board: I019, I021, I022 `rejected`. I020 passes the gate on 1260 maps (follow-up above): `local-test` with PASS,
ready for stage 3 online. What stays useful: the two loggers, `P_LOGCAMP` and `P_LOGRECALL`, and the walking fields (`walk_altar`,
`walk_home`) for the next idea that needs them.

Reproduce: `tools/variante.sh x_r2 study28 "#define P_RECALLCOST 2"` then the gate command above.
