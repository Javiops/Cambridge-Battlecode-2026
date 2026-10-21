# Quiet channel cover: topdraft v14

The complete v87 field batch exposed delivery loss as well as acquisition loss.
In contest versus Cozy A, the team collected 1,200 but banked zero. Native replay
samples show Stellar already at an altar, channeling with 400 gems at rounds
1345/1350/1355; the channel flag is clear by 1360 and the official death/loss
event at 1364 transfers all 400. This is not a failure to start banking. The
same champion repeats a 400-gem loss at 1633. Exact channel cancellation cause
is not decoded. The official handbook confirms tribute takes ceil(gems/10)
turn ends: 400 requires 40. Damage continues it, while stun, death and altar
locking cancel it. See the [official handbook](https://2026a.battlecode.co.uk/game/docs/gems-and-scoring).

V13 tests quiet escort positioning: healthy, empty-handed, noncapturing nearby
allies assemble within two tiles of an actively tributing teammate, retaining
urgent survival and shop priorities. Contact resumes unchanged combat rules.
It fails the large-map economy canary: big-world starter banks 0/34 instead of
v12 692/800, with zero cover logs there. Extra optional ally scanning changes
the trajectory even when no activation appears in periodic logs. V13 is rejected offline,
not uploaded; its exact independent rebuild and 22 full-log games are preserved.

V14 adds one cheap public-geometry rejection before that scan: a channeling ally
within 12 must be at most 13 from a known altar. Farther champions avoid native
ally metadata entirely. No initialization reserve, banking starts/continuation,
contact rules, draft, RNG, observation contract or trained model is changed.
No map/opponent name exceptions are added. V14's source parent is frozen v13;
the functional reference used for evaluation is frozen live topdraft v12.

## Release checks

| Schedule | Starter wins | Reference wins | Faults | Exhausted turns |
|---|---:|---:|---:|---:|
| v14 vs frozen live v12 | 69/70 | 149/302 | 0 | 6 |
| v14 vs fixed v6 | 69/70 | 160/302 | 0 | 6 |

Both broad schedules cover 35 official and 116 generated development maps,
including 16 large layouts, in both seats. The 744 runs are 674 unique fixtures:
70 starter repetitions match exactly. All 22 full-log canaries repeat broad
fixtures and match outcomes and champion statistics. Canary results are 10/10
starter and 9/12 live v12, zero faults/fuel losses. Big-world starter deposits
are 901/932, versus v12 692/800. Diagnostic logs establish quiet cover activation;
they do not isolate its causal contribution from scan/fuel-timing changes.

The ZIP independently rebuilds to the identical frozen release WASM. Original
Stage 1–7 certificates and weights are unchanged. No judge code changed; the
existing 139 passing judge tests remain applicable. The 70 fresh confirmation
maps have zero games played. This is a tested experimental candidate, not a
promotion or proven general strength gain. Preserve v87 and other working
versions for rollback; Fran authorizes automatic experimental upload/activation
with a short note even if aggregate wins initially regress.

Source ZIP SHA256: `6eb3470a10243206ccdfd406634fc9f884438e654c9ea5c3738d98ca26eee1e1`.
Release WASM SHA256: `29b0658fd0b75956baac1eeb864a2b02ed51d2b7973f2525b42afe5ada744f63`.
Official CLI 3.0.2 / rules 1.0.1, pinned build in each result. Deployment state
and actual platform version are recorded separately in CURRENT.json; this
report alone does not claim an upload or server compilation.

Deployment update: **platform v88 is compiled and live**, submission
`359be360-3778-40bf-bf67-a8433dc773f7`. The server-downloaded ZIP matches the
frozen source hash; the server build log and active LIVE status are saved.
V87 remains available for rollback. No server binary hash is claimed. Last
observed unranked allowance is zero, and no v88 games have been requested by
this agent yet. The existing 15-minute heartbeat will use returning quota
with the paired cover-live-plan.json and verify every queued version.
