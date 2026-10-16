# Native assembly checks

The two runners test different scopes. Both preserve copied production headers,
the compiled fixture source, module/replay hashes, the SDK hash, native faults,
fuel pauses and every failed case. They require the reviewed SDK2.2.2 and local
CLI/native engine0.0.2. No network or Battlecode account is used.

```
python tools/tactics-v1-validation/run_native_assembly_budget.py --cli CAMBC --project ARENA --source bots/tactics-v1/src --output NEW_OUTPUT_DIRECTORY
python tools/tactics-v1-validation/run_native_assembly.py --cli CAMBC --project ARENA --source bots/tactics-v1/src --output OTHER_NEW_OUTPUT_DIRECTORY
```

`ARENA` is an existing local CLI project with the official `sdk/` directory.
Use an unused output directory; source files must stay frozen for the run.
The CLI builds a separate fixture bot and uses its normal local compiler cache.

## Controlled entry budget

`native-assembly-budget.cpp` uses explicit projected actors/claims/positions and
kits under an initialized real SDK. Projected actions are **never executed**.
It tests a finite priced invitation at65k fuel, coordinator pending Move at80k,
current readiness and a production farming first-hit proposal at65k, missing
helper and stale-camp negatives, unpriced gold rejection, unsupported-kit unknown,
and a long forecast that must stop unknown while retaining useful action reserve.
This is not physical rendezvous, actual payout, crew optimality or strength proof.

## Physical bodies and capture

`native-assembly.cpp` uses actual Vendetta/Willow bodies, real public geometry,
actual legal movement, native shared claims and no projected World values.
Scripted preparation clears a harmless gold cluster, buys one actual30gold Health
shard and heals at spawn. Both bodies then take real contribution positions.
Production current local readiness controls an actual gateway first hit, followed
by scripted legal allied healing/damage, actual clear and capture payout.

The fixed32×32 public-editor map contains an elk, harmless preparation/alternative
clusters and a reachable hole detour. A real priced producer/rally is logged
separately; it must not be inferred merely from a successful physical readiness
case. Teammate movement and subsequent clear are scripted, so the fixture does
not establish global production farming arbitration or competitive improvement.
The current committed map SHA256 is
`1ba7731349d9e84cbb02943c00537c20671e9cb75933bd3156b550006c8475a9`.

Budget-capped long real clears can legitimately return unknown. A short funded
positive and a safely declined long case are separate required observations;
neither licenses unsupported future helper DPS.
