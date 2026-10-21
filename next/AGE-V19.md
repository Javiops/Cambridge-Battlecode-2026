# Shared join age: topdraft v19

v92 completed 250 native-verified unranked games. Shared release fixes the
selected first-cycle coordination problem, but the Preyas elk A replay shows
Stellar joining at 560 after an authorization at 516. It is dead at the beginning
of 516, 517 and 540; at 560 two teammates are dead and others scattered. This
does not prove that the late join caused a death. The 44-round value is decision
age, not the unlogged first receipt age in v18.

v19 allows a propagated join only within 16 rounds of its first receipt. Older
cached receipts fall through to normal local assembly and quorum checks. Join
logs include receipt round and age; stale rejections log once per unit/campaign.
The 16-round limit was predeclared before running these fixtures. It does not
change local authorization health/quorum, clock, survival, combat, banking, draft,
RNG, model or initialization reserve. Two-round delivery protection and direct
local danger detection remain. No new map or opponent name exceptions.

An old tag first observed after late initialization/reset can still look recent.
Already-latched local release after a later death is outside this experiment.
Rejecting an old message alone does not establish better play.

## Release evidence

Across 35 official and 140 generated development maps, both seats, v19 scores
69/70 starter and 173/350 parent v18, zero faults and four exhausted turns.
All 26 full-log canaries exactly repeat broad outcomes, rounds, picks, team and
champion statistics: 12/12 starter, 7/14 parent, zero faults, one repeated fuel
loss. Big-world starter banks 868/773 with zero fuel exhaustion. These 494 new
runs cover 468 unique fixtures. The frozen ZIP independently rebuilds to the
identical release WASM. Only main.cpp and the new age constant in params.h differ
from v18; all existing parameter values and model source hashes remain intact.

On 24 generated sole-objective fixtures against the same frozen v6:

| Metric | v18 | v19 |
|---|---:|---:|
| Wins | 10/24 | 10/24 |
| Mean bank | 225.08 | 242.08 |
| Mean fresh camp gems | 241 | 267 |
| Mean deaths | 32.79 | 34.29 |
| Zero fresh-gem games | 4 | 3 |
| Fresh before round 350 | 8/24 | 8/24 |
| All units released in first campaign | 24/24 | 24/24 |
| Shared joins | 512 | 511 |

All 511 v19 joins have prior same-cycle, same-group valid quorum authorization
and measured receipt ages at most 13 (the allowed maximum is 16). Nine stale
rejections have ages over 16 and return to local assembly. The descriptive count
of joins more than 16 rounds after the latest logged authorization is 6 in v18
and 0 in v19; that comparison is not a measurement of v18 receipt age.
Logged decisions do not establish arrival, damage, capture or safe depositing.

All 24 split controls have identical parent outcomes, rounds, team, collection
and inventory summaries, with no release/join/stale events. All 48 feature games
have zero faults/fuel losses. Parent feature captures are historical controls,
not additional new v19 runs. Deposits improve locally while deaths rise; there
is no calibrated strength gain or promotion claim.

## Deployment boundary

Eligible for Fran's functional experimental live trial. Keep v92 rollback for
compile failure, persistent faults or stalled play; lower wins alone are not a
trigger. Formal promotion still governs the lab champion. No confirmation maps
were played; all 70 fresh reserved maps and original Stage 1–7 models/certificates
remain intact. The judge was not changed; the separate prior runner correction
already passed 142 tests.

These checks use official 1.0.1/build c3e9ffc8. The current official Windows
distribution still shows the identical CLI 3.0.2 checksum; save its UI evidence
with the deployment. The 1.0.2 announcement is separate. Verify actual server
builds before comparing field cohorts and revalidate under a distributed new
runtime when available. This offline report alone makes no upload/server-binary
claim; read CURRENT.json and the deployment journal.

Source ZIP SHA256: `94cafc9c3bbe99deaf3a169ec236f4ef2a3e0f28b02c1776ef12aea60b7190b7`.
Local release WASM SHA256: `301031fc5a4d34b5ddd263605485a349007e54e7ac8817e0a342307c9457851b`.
