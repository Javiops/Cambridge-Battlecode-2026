# V92 shared rally release: field results

**v92 / topdraft v18 is compiled and live.** All 50 requested unranked groups,
250 games across 35 maps and both seats, are collected and native-verified:
**77 wins, zero faults, one fuel-exhausted turn**. The allocation was 160 nearby,
70 stretch and 20 leader games. No requests have unknown outcomes or remain
uncollected. Automatic ranked and incoming games are separate.

Actual allowance was zero at request end (2026-10-21T03:43:27.045Z) and again
at the read-only check (2026-10-21T04:05:03.923Z). Current team rank is #186,
1637 Elo. That is the primary current rank, not peak rank. Unranked tests
do not change Elo; this window does not establish a cause for ranked movement.

## What changed and what was verified

v18 shares an existing successful rally quorum decision. Each instance remembers
receipt before dead, shopping, healing and banking early returns. Eligible allies
can join that authorized campaign without repeating the same local quorum count.
Byte 7 protects a newly received release for two rounds before normal danger
broadcasts resume. Direct local danger detection, health thresholds, quorum,
clock, survival, banking, draft, model, RNG and initialization reserve remain.

The frozen source ZIP independently reproduces the local release WASM exactly.
The server-delivered source, successful build log, LIVE status and every queued
and completed version 92 are verified. No server binary hash is claimed.
All 250 actual games use official 1.0.1/build c3e9ffc8. The announced 1.0.2
balance changes are separate; these are not 1.0.2 validation results.

## Matched results

The 140 pinned v91 map/opponent/seat pairs score **46 current wins versus 49
previous wins**. All 140 actual seeds match. The other 110 new matchups are
excluded from this comparison. Multi-camp terminal, team, collection and held
inventory statistics match exactly in 86/122 pairs. The other 36 differ; do not
claim universal preservation or opponent binary parity. Opponent WASM hashes
are not exposed. This is development evidence, not promotion or a strength gain.

Across 18 matched single-objective games:

| Metric | v91 | v92 |
|---|---:|---:|
| Wins | 4/18 | 2/18 |
| Mean deposits | 325.00 | 314.28 |
| Mean fresh camp gems | 317.33 | 325.33 |
| Mean deaths | 42.39 | 46.50 |
| Zero fresh-gem games | 4 | 3 |
| Mean credited sole-group clears | 3.22 | 3.72 |
| All units released in the first campaign | 5/18 | 18/18 |
| Mean fraction of units released | 87.04% | 100.00% |

All 427 logged shared joins in this matched subset follow a prior valid quorum
authorization for the same campaign and group. A join log proves a decision,
not arrival, damage, capture or safe depositing. Fresh collection and credited
clears use official events targeting the sole gem group's public campGroup ID;
global monster damage is not attributed to that objective.

## Next specific failure

In Preyas elk A, Stellar now joins at round 176 after the valid quorum at 175,
where v91 still rallied at 200. The team banks 36 with 20 deaths, but collects
no fresh objective gems and receives no credited sole-group clear. That first
coordination defect is fixed without solving objective farming.

The same replay shows a later decision at 516 followed by Stellar's join at 560.
Native own-unit probes show Stellar dead at the beginning of 516, 517 and 540.
At 560 it is healthy at (7,30), while Cassi and Issac are dead and the other
units scattered. These are beginning-of-round snapshots, not exact later unit
inputs. They do not prove the late join caused a death. The 44-round value is
the age of the authorization; v18 does not log exact receipt age.

Test one next change: allow a propagated join within 16 rounds of first receipt;
older receipts fall through to normal local assembly and quorum checks. Preserve
prompt joins and existing health, clock, survival and banking rules. Log receipt
age and rejected stale joins. Late initialization or an already-latched local
release after death remains outside that test. See the predeclared hypothesis
in experiments/shared-release-age-hypothesis.md. Do not also disable campfoe or
change the draft. No new map or opponent name exceptions.

## Release foundation

SHARED-V18.md records 494 new release runs, 468 unique fixtures: 69/70 starter,
172/350 parent, zero faults and four broad exhausted turns. All 26 full-log
canaries repeat exactly. Big-world starter deposits are 868/773, with no fuel
exhaustion. On generated sole-objective fixtures, all-unit first-cycle release
improves 15/24 to 24/24 and deposits 197.33 to 225.08, while wins fall 12 to 10
and deaths rise 31.71 to 32.79. Split controls match 20/24 exactly with no joins.

No confirmation maps were played. All 70 fresh reserved maps and original
Stage 1–7 models/certificates remain intact. v91 remains a rollback for compile
failure, persistent faults or stalled play; lower wins alone are not a trigger
under Fran's authorization for functional experiments.
