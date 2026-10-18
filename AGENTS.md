# Coding assistant instructions (Codex and Claude)

These are the shared instructions for work on the new `bots/foundation` bot.
Other bot generations are reference material; do not silently apply foundation
architecture to them. Use English for all new or edited prose, comments and names.
Translate legacy wording when bringing it into the foundation.

## Read first

1. [Human quick start](bots/foundation/README.md).
2. The relevant topic in the [tactics handbook](docs/tactics/README.md).
3. [Decision contract](docs/tactics/cycle-decision-contract.md) for mission selection;
   its status is Planned, so do not assume arbitration is already implemented.
4. `bots/foundation/src/actions.h` and its tests before changing action behavior.

## Safe scope and collaboration

- Work on a task branch from the team's foundation branch, currently
  `fran/foundation-baseline`. Do not overwrite a teammate's changes.
- Keep the 25 bot source trees in `bots/foundation/baseline.json` unchanged.
  Never regenerate that manifest merely to make a failing check pass.
- Keep each PR focused on one idea. Agree interface changes with the affected
  teammates first. The four work areas are runtime/adapters, cycle/navigation,
  combat and evaluation; require teammate review before merging.
- Do not upload, activate or replace the competition bot without explicit team
  authorization. Do not commit credentials, generated SDKs, binaries or `out/`.
- The scaffold holds position. The live uploaded artifact is unverified; a source
  hash or passing contract test is not proof of live identity or stronger play.

## Implement an idea

1. Write or update its tactic first, keeping the stable topic ID. Include the
   trigger, proposed action, abort rule, fallback and observable expected result.
   Distinguish a proposal from an implemented and measured policy.
2. Add a failing regression scenario for the intended behavior or bug, then
   implement the smallest change under `bots/foundation`.
3. Keep policy separate from engine mutations. During gameplay, only
   `src/sdk_actions.h` calls mutating SDK actions; draft/end-turn lifecycle calls
   stay in `main.cpp`. Policies submit requests through the executor.
4. Obtain a fresh snapshot with `Executor::observe()`, attach its epoch to the
   request, call `Executor::execute()`, and handle the explicit `Outcome`.
   Re-observe before the next request. Rejected attempts invalidate sibling
   requests. Movement, channel start and channel completion are different events.
5. Preserve active channels; cancellation requires an explicit policy and an
   extension of the action contract with tests. Use personal vision only. Never
   infer shared ally vision or private state from omniscient replay fixtures.
6. Bound work by fuel. The 12,000 reserve is an initial guard, not a proven bound
   for new features. Verify new action paths in metered guest tests.

## Validate and hand off

From the repository root, with Python 3.12+, Node 24 and C++20 available:

```sh
pip install cambc==2.2.5
cambc init --yes
python bots/foundation/check.py
```

Windows/wasi-sdk: add `--wasi-cxx <path/to/clang++.exe>`. Optional overrides are
`--cli <path>` and `--engine <path>`. Never skip missing tools, weaken assertions
or silently change the CLI/engine pins. Review mechanics before repinning.
The check covers frozen sources, executor contracts, controlled engine scenarios
and full metered guest games; evidence is `out/foundation/checks.json`.

Competitive changes also use the [team harness](harness/README.md); do not tune on
sealed holdouts. Link the tactic, scenario, command and results in the PR. State
what is still unimplemented and any checks you could not run. Update the short
human guide when usage changes; keep detailed assistant rules in this file.
