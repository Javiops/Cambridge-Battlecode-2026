# Brief for whoever takes an idea (a person or a Claude thread)

Copy this into the thread or the PR when you start. Anything not in here is not part of the job.

- **Idea:** I### <title> (`python3 tools/idea.py show I###`)
- **Hypothesis to check:** <scorecard number, from what to what, on which maps>
- **Kind and gate:** `farm` (fresh maps in favour with p<0.05) | `fight` (not worse locally; online decides) | `bug` | `macro`
- **Base bot:** `bots/study28` on `main` (commit <sha>)
- **Branch:** `idea/I###-short-name`
- **One change:** <the rule / the threshold / the switch>. If another improvement shows up on the way, it becomes a new idea, it does not go in here.
- **Do not touch:** other people's branches; `maps_hold60`/`maps_dev200` are never used for tuning.
- **Time box:** <hours>. If it does not pass the gate by then, deliver it anyway with the number and close it as `rejected`.

## Deliver

1. The branch with the bot diff (only `bots/study28/src`, plus `params.h` if it is a switch).
2. `python3 tools/gate.py bots/study28 main --kind <kind> --idea I###` on the final candidate; attach `out/gate/.../gate.txt`.
3. The 3 worst counterexamples watched with `cambc view` and one line about each.
4. `docs/I###-name.md` following `harness/templates/result.md`, and the PR (draft until the online decision).
5. Board: `idea.py set I### --stage local-ok|local-test|rejected --pr <n> --note "<the number that decides it>"`.
