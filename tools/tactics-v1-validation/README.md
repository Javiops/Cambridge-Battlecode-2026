# Tactics v1 correctness checks

The fixtures call the production policy helpers. No account, API token or network is needed. They use explicit failure paths, so assertions still run under release settings. Most of the policy count is exhaustive claim-codec boundaries; it is not thousands of independent game scenarios.

Use Python 3.10+, Node.js with the WASI/exnref support tested in Node 24, and WASI SDK 33 / Clang 22.1.0 supplied by official CAMBC 2.2.2. Configure `WASI_SDK_PATH` to the SDK root or provide `--compiler`; provide `--node` if Node is outside PATH.

From the repository root, assuming this directory is `tools/tactics-v1-validation`:

```powershell
python tools/tactics-v1-validation/run_tests.py --source bots/tactics-v1/src --compiler C:/path/to/wasi-sdk-33/bin/clang++.exe --node C:/path/to/node.exe --sdk-root C:/path/to/cambc-project/sdk --output work/tactics-v1-checks
```

Omit `--sdk-root` for only SDK-free policy/combat/squad/channel/recovery/delivery checks. The channel, recovery and delivery fixtures insert exact production functions into deterministic narrow world inputs; they do not simulate native movement or channel timing. Supply `--sdk-root` to compile every production header independently and together against the reviewed SDK. The script records source, fixture, module and tool hashes and rejects changing source during a run. Review the explicit SDK pin before upgrading to another version.

For native action activation and fuel behavior, initialize a separate project with the official CLI and run a small explicit map list, both sides:

```powershell
python tools/tactics-v1-validation/run_integration.py --cli C:/path/to/cambc.exe --project C:/path/to/cambc-project --candidate bots/tactics-v1 --opponent C:/path/to/reference-bot --maps C:/path/to/compact.map26a C:/path/to/long.map26a --output work/tactics-v1-integration
```

`CAMBC` or PATH can provide the CLI. `--project` explicitly selects its SDK/configuration. The Windows CLI 2.2.2 first-release-build workaround generates a normal compile database before release compilation; only release modules play. Native results must report engine **0.0.2**. These commands only build and run local files and never submit or queue matches.

Inspect actual `statistics.json` events for collection, completed tribute, purchases, ward placement, deaths and `fuelExhausted`. Keep candidate and opponent errors separate. A zero-fault game may still reveal starvation or a tactic never activating. Match outcomes are descriptive integration evidence; they do not establish ladder superiority or optimal thresholds.

The native dash gateway regression uses the same official CLI/project and the
three checked-in map fixtures:

```powershell
python tools/tactics-v1-validation/run_native_dash.py --cli C:/path/to/cambc.exe --project C:/path/to/cambc-project --source bots/tactics-v1/src --output work/tactics-v1-dash
```

It checks an SDK range mask that includes a wall-separated target, rejection by
the production gateway before an invalid SDK action, a subsequent legal dash,
hole crossing, and a legal bent path around a single wall. Both sides must pass,
with zero faults and zero fuel exhaustion. SDK `ability.valid_tiles()` is a
range mask; it does not certify a dash path or legal landing.

Freeze source before using untouched generated geometries. If a functional defect requires a change, retain the failed result and exact version, repair it, and label reused cases as development evidence. Fine tuning belongs to a later experiment.

The purpose-built native lifecycle regression tests the two SDK integration failures discovered during implementation. It constructs enemy handles while hidden, meets the enemy and inspects refreshed kit metadata, collects 35 gold, dies to an elk, buys a 30-gold component while dead, checks the 5-gold wallet and inventory, and observes a fresh respawn. Run it against the actual production headers:

```powershell
python tools/tactics-v1-validation/run_native_lifecycle.py --cli C:/path/to/cambc.exe --project C:/path/to/cambc-project --source bots/tactics-v1/src --output work/tactics-v1-native-lifecycle
```

The script materializes exact header copies so the CLI tracks their dependencies, requires all three stage markers on both sides, and rejects native faults, caught errors or fuel exhaustion. Its scripted behavior is regression evidence and has no competitive-strength interpretation. Native capture/recall timing and ward placement are separate scenarios.

The native ward regression supplies a scripted Travel mission to the actual production ward policy. It verifies native placement acceptance, the body's own ward position and cooldown, and one native placement event per side, with no faults, caught errors or fuel exhaustion. It isolates policy/API activation and does not claim the main coordinator schedules a ward in every game:

```powershell
python tools/tactics-v1-validation/run_native_ward.py --cli C:/path/to/cambc.exe --project C:/path/to/cambc-project --source bots/tactics-v1/src --output work/tactics-v1-native-ward
```
