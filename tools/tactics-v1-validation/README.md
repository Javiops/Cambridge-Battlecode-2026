# Tactics v1 correctness checks

The fixtures call the production policy helpers. No account, API token or network is needed. They use explicit failure paths, so assertions still run under release settings. Most of the policy count is exhaustive claim-codec boundaries; it is not thousands of independent game scenarios.

Use Python 3.10+, Node.js with the WASI/exnref support tested in Node 24, and WASI SDK 33 / Clang 22.1.0 supplied by official CAMBC 2.2.2. Configure `WASI_SDK_PATH` to the SDK root or provide `--compiler`; provide `--node` if Node is outside PATH.

From the repository root, assuming this directory is `tools/tactics-v1-validation`:

```powershell
python tools/tactics-v1-validation/run_tests.py --source bots/tactics-v1/src --compiler C:/path/to/wasi-sdk-33/bin/clang++.exe --node C:/path/to/node.exe --sdk-root C:/path/to/cambc-project/sdk --output work/tactics-v1-checks
```

Omit `--sdk-root` for only SDK-free policy/combat/squad checks. Supply it to compile every production header independently and together against the reviewed SDK. The script records source, fixture, module and tool hashes and rejects changing source during a run. Review the explicit SDK pin before upgrading to another version.

For native action activation and fuel behavior, initialize a separate project with the official CLI and run a small explicit map list, both sides:

```powershell
python tools/tactics-v1-validation/run_integration.py --cli C:/path/to/cambc.exe --project C:/path/to/cambc-project --candidate bots/tactics-v1 --opponent C:/path/to/reference-bot --maps C:/path/to/compact.map26a C:/path/to/long.map26a --output work/tactics-v1-integration
```

`CAMBC` or PATH can provide the CLI. `--project` explicitly selects its SDK/configuration. The Windows CLI 2.2.2 first-release-build workaround generates a normal compile database before release compilation; only release modules play. Native results must report engine **0.0.2**. These commands only build and run local files and never submit or queue matches.

Inspect actual `statistics.json` events for collection, completed tribute, purchases, ward placement, deaths and `fuelExhausted`. Keep candidate and opponent errors separate. A zero-fault game may still reveal starvation or a tactic never activating. Match outcomes are descriptive integration evidence; they do not establish ladder superiority or optimal thresholds.

Freeze source before using untouched generated geometries. If a functional defect requires a change, retain the failed result and exact version, repair it, and label reused cases as development evidence. Fine tuning belongs to a later experiment.
