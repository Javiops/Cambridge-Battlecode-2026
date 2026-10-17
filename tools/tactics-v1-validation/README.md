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
hole crossing, and a legal bent path around a single wall. A fourth game uses
Cassi and Issac: Cassi occupies the unique diagonal midpoint, Issac's blocked
dash preserves position and cooldown, and an alternative dash still succeeds.
Cassi also reduces actual remaining fuel to 11,000 and verifies that the final
mutation gate declines Recall without publishing a channel attempt. Both sides must pass,
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

The farming-policy regression runs the actual production farming function with explicit World projections under initialized native SDK geometry. It checks that a suppressed incumbent cannot displace a productive alternative, that a first clear arrival after long travel is not classified as existing attack stagnation, and that a ready gem job with zero deadline value cannot erase an unready positive-value job. It does not execute the projected camp attack or claim a physical payout:

```powershell
python tools/tactics-v1-validation/run_native_farming.py --cli C:/path/to/cambc.exe --project C:/path/to/cambc-project --source bots/tactics-v1/src --output work/tactics-v1-farming-policy
```

The native capture/recall/tribute timing regression is documented in [NATIVE-CYCLE.md](NATIVE-CYCLE.md). Its scripted owner loop and the full competitive bot are separate modules. Preserve that distinction when interpreting its assertions.


The native shopping regression physically earns 315 gold, buys a real initial item,
then calls the production elective-return planner with 65,000 remaining fuel. Two
bounded advisory opportunities prepare immutable geometry; the funded plan names
one actual affordable bundle and a gem job separate from its original gold job.
It recalls, buys the exact bundle, verifies the private wallet and installed power,
then physically clears the newly certified 2400 HP resource, captures and banks 36 gems,
and returns to full spawn health. Both sides require zero faults and fuel pauses.

```powershell
python tools/tactics-v1-validation/run_native_shopping_gem.py --cli C:/path/to/cambc.exe --project C:/path/to/cambc-project --source bots/tactics-v1/src --output work/tactics-v1-shopping-gem
```

This uses a scripted tactical loop with actual production shopping, solo forecast,
World and mutation gateway. It does not run the full production arbiter or establish
competitive strength. The old same-camp reserve certificate rejects the old kit;
that is a model-scoped policy decision, not proof that every possible tactic fails.
The future quiet resource schedule is revalidated on actual arrival. Pure suites
`shopping-gem` and `shopping-investment` separately check the same projection,
completed-trip pricing, strict deadlines and exact successful/failed receipts.


Lethal-peel eligibility and native budget regression
---------------------------------------------------

`combat-peel` checks the production eligibility helper against the former per-ally predicate, including ready rights, actual range boundaries, control immunity/extension and reflected self-lethal casts. The native reproducer extracts the exact production peel block and its `take` callback while retaining production World/risk/action code:

```powershell
python run_native_peel.py --cli /path/to/cambc --project /path/to/arena --source ../../bots/tactics-v1/src --output /path/to/new-results
```

Add `--baseline-source /path/to/frozen/old/src` for the same-scenario section-cost comparison. The physical scenario earns an actual 20HP threatened ally through native attacks, checks the out-of-range SDK rejection, and executes the legal control cast. Empty-enemy and immune-enemy cases are explicitly marked World projections. This isolates the peel subsection and does not establish full-arbiter activation or match strength. Output pins source/module/map/SDK/replay bytes, and reports all native faults and fuel exhaustion.


Finite zero-wallet investment regression
----------------------------------------

`shopping-cash` runs 33 exact finite itinerary and wallet/capture-receipt checks. `shopping-cash-hint` runs 12 exact route-cache contract checks: a contribution-stage field cannot replace the actual cash-camp-rooted field required by the consumer.

**Source scope:** the old Wolf-unlock native scenario below is obsolete after the solo
camp-phase correction in integration20. Cassi can already clear that Wolf without its
formerly required Health shard; do not force a purchase or interpret that old fixture's
assertions as competitive-module faults. Use the separate partial-emblem native case:

```powershell
python tools/tactics-v1-validation/run_native_cash_partial.py --cli C:/path/to/cambc.exe --project C:/path/to/arena --source bots/tactics-v1/src --output work/native-cash-partial
```

This case physically earns 210 gold and buys four Jungle Health plus three Power Health
shards in a scripted prelude. With its real wallet then empty, unchanged main must earn
the next 35 gold, buy the fifth Jungle Health shard, clear the named Elk and actually bank
36 gems. No wallet/stat projections enter main. One controlled starting kit is activation
evidence; it is not competitive-strength or general opening-allocation proof.

```powershell
python run_native_cash_investment.py --cli /path/to/cambc --project /path/to/arena --source ../../bots/tactics-v1/src --output /path/to/new-results
```

The producer uses actual65k entry, official cash35/Wolf22 rewards, and no sandbox income. The separate full-main scenario calls production `Bot::turn` for Cassi while Issac idles at spawn, then requires actual cash capture -> exact30gold Health purchase from wallet35 -> named Wolf capture -> actual22gem bank. The main fixture is48tiles wide to keep the initial quiet investment separate from enemy contact. Later play may encounter opposition; the first finite conversion is the assertion, not match strength. Both fixtures use one draft pick to isolate this native contract and are not tournament map samples. All failed development records are retained separately.

Native survival-budget caller regression:

```powershell
python tools/tactics-v1-validation/run_native_survival_budget.py --cli <cambc.exe> --project <project-with-pinned-sdk> --source bots/tactics-v1/src --output <new-output-folder>
```

This runs the actual production `choose_mission` with explicit projected personal HP/bag/threat/mission inputs under the native SDK. Fifteen cases per side cover wounded threatened carriers, healthy lethal-contact carriers and capture holders at47k/51k, safe immediate/winning Tribute, unsafe Tribute, spawn healing, live holder retention, harmless raw exposure after mitigation, an affordable current singleton, and shield-bearing owners whose actual HP loss is lethal. The runner requires all30 markers, same owner epoch, a remaining execution reserve and zero native faults/fuel events. No projected action is executed; full-main matches and physical payout are separate evidence. Current shield is subtracted once; multi-owner forecasts credit it only when its known duration covers the horizon.
