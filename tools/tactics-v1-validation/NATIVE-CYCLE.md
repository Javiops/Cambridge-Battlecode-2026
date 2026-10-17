# Native capture, normal recall and tribute check

This local scripted fixture uses unchanged production headers, including `overlap_hold`, `current_recall_ticks`, `current_tribute_ticks`, `observe_progress`, `observe_hold`, `remember`, `World.refresh` and the action gateway. Its main function controls the experiment; it does not test the full production arbiter or strategy strength.

From the repository root:

```powershell
python tools/tactics-v1-validation/run_native_cycle.py --cli C:/path/to/cambc.exe --project C:/path/to/initialized-cambc-project --source bots/tactics-v1/src --output work/native-cycle-result
```

Use the reviewed official CAMBC SDK 2.2.2. The runner checks its header hash and the actual completed game's engine version 0.0.2. CAMBC's normal compiler caches must be writable. The output directory must be new. No server submission or network request is made.

On the committed controlled single-tile wolf map, both mirrored bodies clear their own camp, then demonstrate:

1. Starting normal recall with no prior capture hold interval departs before payout and receives no gems.
2. Returning and retaining the production helper's required prior hold interval before normal recall preserves the 22-gem payout by departure.
3. An accepted tribute starts with the 22 gems still carried and score unchanged. The later actual completion empties the bag, increases public score by 22 and is recognized by the production observer.

The runner retains source, fixture, SDK, CLI, compiled fixture-module, map, replay and statistics hashes. It requires actual phase markers, matching production completion observations, one 22-gem collection and submission per body, zero native faults and zero fuel exhaustion. Integer resource counts are read from statistics `value`; their separate floating `amount` field is zero.

Home, enemy contest, damage interruption and the pending-zero interval between engine phases are outside this particular fixture. Separate mechanics evidence and policy fixtures cover those boundaries. This fixture's module is different from the competitive bot module, even when its copied production headers match.

The map is committed with its SHA-256. Optional regeneration uses the pinned official viewer engine and Node.js WASI:

```powershell
node tools/tactics-v1-validation/generate_native_cycle_map.mjs C:/path/to/v0_0_2-DFj19m76.wasm
```
