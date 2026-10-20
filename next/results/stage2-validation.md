# Stage 2 baseline acceptance: PASS

Validated on 2026-10-20 with the pinned CLI/SDK 3.0.1 runtime.
The complete regression suite reports **69 passed**, with no skips.

| Check | Result |
|---|---|
| Frozen plan | 24 release slots, eight screening maps; family/lineage split fixed before outcomes |
| Admitted games | 23, with zero faults or fuel exhaustion |
| Quarantine | one complete v76 mirror on g1-screen-004, one team-B fuel-exhausted turn; no labels admitted |
| Actor frames | 104,133, sampled every fifth round from complete trajectories |
| BC tensors | 44,221 train + 15,070 validation = 59,291 eligible examples |
| Teacher filtering | idle context retained; idle decisions excluded from BC |
| Split integrity | no map, map-family or teacher/opponent lineage overlap |
| Replay differential proof | 2,560 first actor frames and all accepted action sequences match release SDK logs |
| Full data audit | encodings recomputed; every eligible tensor/label/mask checked against its actor row |
| Live sparring | four newly requested unranked groups, 20 completed games, both seats, no confirmation maps |
| Live results | v76 0–10 vs Nyx; 0–10 vs Sneaky Bush Campers |
| Online terminal proof | all 20 native replay winner/round/banks agree with website evidence |
| Missing replay fields | guest memory and boolean returns remain null; v1 model does not consume them |
| External admission | online replays are diagnostics; exact server-build/opponent-WASM identities are unavailable |
| Next stage | Stage 3 training has not started |

The action distribution and champion coverage limits are explicit in STAGE2.md. A
constant-wait classifier reaches 56.9% validation accuracy. Training covers seven body
types, and the first dataset lacks Willow and Heart. This is a measured baseline,
not final strong-opponent qualification.

Machine evidence: `stage2-plan.json`, `stage2-dataset.json`, `stage2-replay-proof.json`,
`stage2-audit.json`, `stage2-online.json`, `stage2-ready.json`. The manifest and actual
shards live in `datasets/stage2-baseline-v1/` and the delivered data ZIP.
