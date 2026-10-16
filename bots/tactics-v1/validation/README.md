# Tactics v1 validation

This is a new implementation for review, based on the tactics specification at commit 20c97a701bc9ddb45a23951e6ea28a79f7f22df9.

## Local integration

Frozen release artifact: **0 wins, 16 losses, 0 draws** in 16 games against the pinned study27-economy snapshot.
Four official geometries and four generated geometries were played from both sides. Generated layouts were frozen before the first candidate outcomes, then used to find integration defects. They are development integration cases, not an untouched final strength holdout. These results are descriptive, not evidence of ladder superiority.

Candidate: **0 native faults, 0 caught exceptions, 0 action API error codes**. Native fuel-exhaustion events: **290**. An exhausted computation can resume in a later owner epoch; the mutation and claim gateways reject stale epochs. Any nonzero fuel count remains a performance limitation.

| Map | Side | Result | Gems | Clears / banks | Native fuel pauses |
| --- | --- | --- | --- | --- | --- |
| fragment | A | L | 366:1012 | 17 / 15 | 3 |
| fragment | B | L | 358:1034 | 15 / 12 | 4 |
| lanes | A | L | 88:1018 | 9 / 4 | 18 |
| lanes | B | L | 0:1040 | 7 / 0 | 18 |
| expanse | A | L | 66:1050 | 20 / 3 | 44 |
| expanse | B | L | 110:1010 | 20 / 5 | 47 |
| corners | A | L | 22:1024 | 10 / 1 | 50 |
| corners | B | L | 0:1002 | 13 / 0 | 56 |
| fresh-compact-open | A | L | 372:1020 | 18 / 12 | 1 |
| fresh-compact-open | B | L | 328:1014 | 19 / 12 | 16 |
| fresh-long-two-crossings | A | L | 374:1014 | 25 / 13 | 10 |
| fresh-long-two-crossings | B | L | 396:1014 | 27 / 14 | 7 |
| fresh-wide-detours | A | L | 88:1008 | 19 / 3 | 5 |
| fresh-wide-detours | B | L | 220:1008 | 27 / 8 | 6 |
| fresh-sparse-gold-heavy | A | L | 276:1008 | 5 / 6 | 3 |
| fresh-sparse-gold-heavy | B | L | 168:1020 | 4 / 5 | 2 |

## Scope of correctness evidence

The portable policy runner exercises actual production helpers for claim encoding, combat alternatives, minimum sufficient crews, channel threat, recovery, and delivery selection. Most numeric checks are exhaustive claim-codec boundaries; they are not thousands of distinct tactical scenarios. Every production header is also compiled independently against SDK 2.2.2.

Purpose-built native scenarios separately exercise real SDK metadata after an initially hidden enemy becomes visible, death and dead-state shopping, wallet/inventory changes, respawn, ward policy and placement, dash traversal restrictions, normal capture/recall overlap and actual later tribute completion. The occupied-diagonal case also verifies a low-fuel mutation is refused without starting recall or consuming its attempt bookkeeping. Full production farming is called on controlled World projections for failure exclusion, first-clear grace and deadline eligibility. These projections do not simulate every engine state transition. See the native reports for exact scopes and source hashes. Native Home overlap and every possible contested handoff are not covered by these narrow scenarios.

## Remaining limits

The source audit covers all 96 handbook topics and distinguishes implemented behavior, bounded permitted fallbacks, partial strategies, and omitted optional features. It does not label every topic verified. Strategic warning sharing, full route-loop detection, global marginal helper allocation, and explicit territory jobs remain partial. Initial draft, shopping and cycle valuations still use declared fallbacks.

The old opponent has its own caught errors; opponent faults are kept separate from candidate evidence. The local snapshot is not asserted to be the current live upload.

This candidate should be reviewed and tuned before replacing the competitive live bot. No online submission or activation was performed.

## Reproduce and inspect

- [Portable runners](../../../tools/tactics-v1-validation/README.md)
- [Exact source and runtime hashes](source-manifest.json)
- [All 16 final slots](integration-results.json)
- [Production policy checks](policy-tests.json)
- [Source coverage and limitations](implementation-audit.md)
