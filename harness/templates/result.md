# I### <title> (the idea's doc; goes in docs/I###-name.md with the PR)

**Hypothesis:** <which number it moves, from what to what, on which maps>. Source: <scorecard / study / brainstorm>.

**Change:** <one sentence>. Switch: `P_XXX <value>` (base <value>). Files: `bots/study28/src/...`.

## Local gate (`tools/gate.py ... --kind <kind>`)

| phase | result |
|---|---|
| safety | faults 0, broken 0, fuel cand/base <n>/<n> |
| fresh maps | <w>-<l> on both sides out of <n> maps, p=<p>; gems/100 rounds <c> vs <b> |
| panel spar11/12/16 | flips <for>/<against>, p=<p>, veto no |
| verdict | PASS / FAIL (<why>) |

Counterexamples watched (`out/gate/.../counterexamples.md`):
- `<map>`: <why it loses there and whether it matters>
- ...

## Online (`online/lfl.py --a "<version>" --b "<base>"`)

| batch (UTC) | version | games | raw | shared pairings | A only / B only | p |
|---|---|---|---|---|---|---|
| | | | | | | |

Ranked in the window: <w-l>. Online faults: <0>.

**Decision:** accepted / rejected / undecided after <n> hours, with <number>. Board updated: `idea.py set I### --stage ...`.

## What we learned (one or two lines that help the next idea)
