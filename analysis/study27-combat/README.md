# study27 combat experiment

The retained bot is [bots/study27-combat](../../bots/study27-combat). Eleven
isolated variants were screened on 53 exposed maps; two advanced to 253 maps,
then their combination and direct component ablations were tested. The final
tested source/WASM was frozen before generating 1,024 fresh maps (seed
`2154873391`).

Fresh confirmation comprised **14,336 unique physical games**:

| Comparison | Frozen candidate | Original | Evidence |
|---|---:|---:|---|
| Direct study27, both sides | 1,074 wins / 974 losses | — | 139 both-won / 89 both-lost maps; paired sign p=0.001128 |
| Three-spar matched panel | 5,050 / 6,144 wins | 4,889 / 6,144 | +161 (+2.62 pp); 221 positive / 138 negative map deltas; p=0.00001387 |

All seven gates and the independent final audit passed. All three spar
subgroups improved (+63/+42/+56 wins). Zero reported bot faults or observed
reinitializations occurred. Caught SDK errors remain nonzero sampled diagnostics.
The combination's incremental development comparison against AoE alone was
258–248 (p=0.603); fresh evidence applies to the combined unit. These fixed older
spars and procedural maps do not establish current ladder or tournament results.

The current delivered source has one post-confirmation cleanup: remove the
earlier redundant `#define P_U34_RESET_LIVE 1`, retaining the later effective value
`2` as its single definition. The 14,336-game results remain historical evidence
for the frozen source; they were not rerun after cleanup. Separate checks in
`cleanup-validation.json` confirm identical preprocessed C++ and macro environment
and a passing SDK build with the same WASM hash as the historical candidate.
`cleanup-wasm-equivalence.json` separately verifies the complete compiled WASM
bytes are identical. The new source/ZIP hashes
and original frozen identities are distinguished in `source-manifest.json`.

`RESULTS-FINAL.txt` contains detailed outcomes, descriptive combat/gem metrics,
tests and limitations. `source-manifest.json` pins the six current files and ZIP,
historically tested WASM, verdict, audit and cleanup validation.
`study27-combat.patch` is the three-file diff, including parameter cleanup, against
`c462346d4ace741bfd8f5251fb0e5e2eee69b800`.

## Evidence contents and extraction

Keep `export-manifest.json`, `audit.json`, `outcomes.jsonl.gz`, `views.jsonl.gz`,
`maps.zip` and `provenance.zip` together in this directory. Verify every file's
SHA256 against `export-manifest.json` before extraction. `audit.json` separates
26,754 distinct physical inputs: 25,236 new experiment games and 1,518 historical
baseline imports. Repeated stage memberships/cache reuse add no new evidence.
All 14,336 confirmation games are from this experiment; 6,143 completed baseline
games were recovered unchanged after an orchestration interruption.

For a separate initialized C++ project at `$project`, and a new review folder
at `$review`, run from this evidence directory:

```powershell
Expand-Archive -LiteralPath maps.zip -DestinationPath $project
Expand-Archive -LiteralPath provenance.zip -DestinationPath $review
```

`maps.zip` paths already start with `maps/`, `maps_gen/`, `maps_dev200/` or
`confirmation1024/`; extract at the project root, without another maps prefix.
`audit-map-manifest.json` maps names to hashes. `provenance.zip` contains
`sources/<bot>/src/`, candidate records, sanitized immutable stage plans,
selection/freeze/generation/verdict/audit records, harnesses, transforms,
fixtures and `publish-tools/`. Copy each desired `sources/<bot>/src/` directory
to `$project/bots/<bot>/src/`, then build with CLI/SDK 2.1.6. Build/runtime pins
are in the records. Game statistics must report engine 0.0.1/schema 2; the CLI
has no direct engine-file injection option.

For a practical paired smoke test after building both archived bots, run from
`$project` and use an actual extracted confirmation map:

```powershell
cambc build bots/cm_combo_aoe_dash
cambc build bots/original
cambc run bots/cm_combo_aoe_dash bots/original --map confirmation1024/fresh-0000.map26a -o smoke-a --statistics smoke-a.json
cambc run bots/original bots/cm_combo_aoe_dash --map confirmation1024/fresh-0000.map26a -o smoke-b --statistics smoke-b.json
```

For full confirmation, repeat both sides on all 1,024 exact maps for candidate
versus original and spar11/12/16, plus original versus each spar (14 games/map).
Follow archived stage plans, ordered source/WASM/runtime hashes and map-unit
aggregation. A new game series is a replication, not another independent test
of a new hypothesis on unseen maps. The exported harness uses original local
paths; do not run its setup/generation scripts blindly after extraction.

## Recompute the compact score totals without games

Run this from the evidence directory using Python 3. The outcome key joins each
semantic view to one physical simulation; only confirmation views are included.

```python
import gzip, json
from collections import Counter
with gzip.open("outcomes.jsonl.gz", "rt", encoding="utf-8") as stream:
    outcomes = {row["key"]: row for row in map(json.loads, stream)}
totals = Counter()
with gzip.open("views.jsonl.gz", "rt", encoding="utf-8") as stream:
    for view in map(json.loads, stream):
        if not any(s.startswith("confirmation-") for s in view["stages"]):
            continue
        row = outcomes[view["key"]]
        outcome = row["outcome"]
        score = 0.5 if outcome == "draw" else float(
            outcome == ("teamA" if view["side"] == 0 else "teamB"))
        pair = (view["candidate"], view["opponent"])
        totals[pair + ("games",)] += 1
        totals[pair + ("wins",)] += score
for pair in sorted({k[:2] for k in totals}):
    print(pair, totals[pair + ("wins",)], "/", totals[pair + ("games",)])
```

The archived verifier/audit records show the full paired-map calculation.
Compact exports omit full raw statistics and most native replay bytes; raw
SHA256 references remain. Re-running `confirm.py`/`audit_export.py` from scratch
also needs those locally retained stage/cache files and pinned runtime. Compact
score recomputation alone cannot reproduce every raw-cache integrity check.

Generator support in `publish-tools/reproduction-support-pins.json` must be
restored at its original relative paths for imports to work: generator at
`work/study28-fixes/generate-fresh.mjs`, helper at
`work/battlecode-bot-v1/r2-ward/map-variants.mjs`, and reference editor engine at
`work/battlecode-bot-v1/r2-research/v0_0_1-ctH8uuEb.wasm`. Existing maps should be
used for exact outcome reproduction. Do not overwrite the archived cohort.

One historical orchestration-source hash probe conflicts with archived bytes
and two earlier records; the contrary bytes were not retained. That uncertainty
is preserved in `recovery-provenance-addendum.json` and its review. Frozen
source/WASM, runtime/map identities and final row/cache integrity checks passed
separately; continuous historical harness-byte identity is not claimed.
