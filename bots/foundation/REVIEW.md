# Foundation review and Carson Burke comparison

Reviewed 18 October 2026. **Ready as a shared development scaffold.** It still
holds position; neither competitive strength nor a live-upload match is proven.
Runtime/action, policy-conflict, official-engine and metered-guest checks pass.

## Gaps found and fixed

- Added `planner.h` and a policy registry so contributors return proposals through
  one owner instead of independently spending actions or growing `main.cpp`.
  Conflict tests cover priority, stable ties, stale proposals, channels and faults.
- Broadened CI paths to all bot sources, strategy docs and assistant instructions.
  Editing only a frozen bot now triggers its integrity check. CI detects changes;
  a teammate must still review them, and repository rules must enforce reviews if desired.
- Guest builds now use a fresh copy of current modules, preventing deleted files
  from lingering in a test build. Checks reject concurrent changes to source,
  tests, runner or baseline, and verify the CLI game's exact engine build hash.

## What we took from Kaggriculture

Source snapshot: CarsonBurke/kaggriculture at
[`ab1e8819`](https://github.com/CarsonBurke/kaggriculture/tree/ab1e8819d7bab850deb594ff17686dbc81598eca).
These are adapted engineering ideas; no source code or neural model was copied.

| Source idea | Our implementation and limit |
| --- | --- |
| [Official-engine validation and simulator parity](https://github.com/CarsonBurke/kaggriculture/blob/ab1e8819d7bab850deb594ff17686dbc81598eca/README.md#approach) | Pinned official-engine scenarios and full metered games. We have no replacement simulator and claim no complete parity proof. |
| [An action ledger updated after each order](https://github.com/CarsonBurke/kaggriculture/blob/ab1e8819d7bab850deb594ff17686dbc81598eca/README.md#approach) | One executor, explicit outcomes, fresh observations and invalidated sibling requests. The policy selector connects future modules. |
| [Content-addressed provenance](https://github.com/CarsonBurke/kaggriculture/blob/ab1e8819d7bab850deb594ff17686dbc81598eca/src/kaggriculture/provenance.py) | Frozen old sources plus source/test/tool/engine/map/artifact hashes in `checks.json`. Live upload identity remains unverified. |
| [Written proposals and experiment ledger](https://github.com/CarsonBurke/kaggriculture/blob/ab1e8819d7bab850deb594ff17686dbc81598eca/docs/experiments/runs.md) | Existing tactic IDs/statuses, idea board and harness; PRs connect specification, scenario and evidence. |
| [Tough opponents and separate evaluation](https://github.com/CarsonBurke/kaggriculture/blob/ab1e8819d7bab850deb594ff17686dbc81598eca/README.md#approach) | Existing team harness supplies the starting point. A foundation opponent panel, automatic historical-opponent selection and promotion gates are still future work. |

Kaggriculture's behavior cloning, PPO, attention model and privileged critic are
not implemented here. Their usefulness for this fuel-limited C++ game is unproven.

## Team starting point

Use [INTEGRATION.md](INTEGRATION.md) for the module contract and PR base branch.
Runtime owner extends observations/actions; cycle owner adds mission state and
navigation; combat owner adds legal sequences and proposals; evaluation owner
adds scenarios and a frozen opponent panel. Agree the first snapshot/interface
extensions together. Build a complete cycle before judging win rate; do not promote
this holding scaffold or confuse contract correctness with competitive improvement.
