# Paid scalar owner sequence

Run from this frozen validation package against its matching frozen production source:

```text
python native-solo-sequence/run_native.py --cli PATH_TO_CAMBC --project PATH_TO_LOCAL_CAMBC_PROJECT --source PATH_TO_FROZEN_SRC --output NEW_OUTPUT_DIRECTORY --mode positive
python native-solo-sequence/run_native.py --cli PATH_TO_CAMBC --project PATH_TO_LOCAL_CAMBC_PROJECT --source PATH_TO_FROZEN_SRC --output ANOTHER_NEW_DIRECTORY --mode negative
```

The project supplies SDK2.2.2 and the official `maps/lanes.map26a`; the runner checks their hashes and the CLI hash. It builds a copy of the actual production main and headers, plus a quiet opponent, and runs both sides with the default native budget.

The only gameplay-copy delta burns native guest fuel immediately before an **already selected, actually paid** damage continuation. It changes no World, actor, camp, wallet, mission, permissions, or proposal. The main delta emits the buffered measurement after the owner ends. Positive admission is measured between40000 and41000 fuel and must produce an accepted Basic followed by the required damage in that owner. The negative measurement is below40000 and must produce neither first hit nor damage. Missing natural activation fails; the runner never forces a target or a choice.

Reports distinguish the original production main hash from the instrumented main and full copy hashes, retain the actual engine build/seed, module/map/replay/statistics/SDK/CLI pins, native faults, caught errors, API errors, and fuel events. These are controlled budget/consumer correctness checks, not independent strength games. The ordinary unmodified-main panel supplies separate clear/capture/bank activation evidence.
