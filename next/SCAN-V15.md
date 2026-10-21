# Visible ally snapshot scan: topdraft v15

V88's first controlled field test wins 8/30 versus historical v87's 12/30,
with no faults/fuel losses. Paired contest deposits stay at 200 despite cover
activation; elk-arena acquisition varies sharply by opponent and seat. Retain
the usable experiment and fix one concrete scan issue rather than assuming
cover is proven or reverting solely for wins. See V88-FIELD.md.

The old cover loop wraps the entire cached ally roster in one exception handler.
A live hidden ally can end the scan before later visible allies are considered.
Its alive/channel/position methods also issue separate native queries. An
official native replay probe at round 500 of v88 big-world Preyas A confirms:
from actor 0, ally 1 returns visibility error 97, while later allies 2/4/5 are
readable. That frame has no active tribute, so it does not prove a missed escort.

V15 reads one visibility-checked champion record per nonself roster entry. Hidden
entries are skipped; alive, channel and position come from that same record.
This uses the SDK import already used by observe.h, with visibility enforced
by the official engine. No hidden record is consumed after a failed query.
Cover conditions, distances, priority, contact rules, banking, initialization
reserve, draft, RNG, observation contract and trained weights are unchanged.
No map/opponent-name exceptions are added. The source parent/reference is v14.

One call per entry does not guarantee fewer calls per turn: a complete scan can
inspect more entries than the old early exit. Measure farming and runtime as
well as correct visibility handling; do not infer strength from cleaner code.

## Release evidence

| Schedule | Starter wins | Reference wins | Faults | Exhausted turns |
|---|---:|---:|---:|---:|
| v15 vs frozen v14 | 69/70 | 149/302 | 0 | 10 |
| v15 vs fixed v6 | 69/70 | 143/302 | 0 | 5 |

Both schedules cover 35 official and 116 generated development maps, including
16 large layouts, in both seats. The 744 runs contain 674 unique fixtures;
70 starter repetitions and 22 full-log canaries match outcomes and champion
statistics exactly. Canary results are 10/10 starter and 5/12 v14, no faults,
one reference fuel loss. Big-world starter deposits are 876/948, both wins with
zero exhaustion, versus v14 901/932. No lab promotion or general strength claim.

The frozen source ZIP independently rebuilds to the identical local release
WASM. Original Stage 1–7 certificates, trained model files and consumed holdout
locks remain intact; 70 fresh confirmation maps have zero games played. No
judge code changed; prior 139 passing judge tests remain applicable. Fran
authorizes automatic functional experimental uploads with short notes; actual
platform identity, source delivery, compilation and queued versions must be
verified separately. Keep v88 and earlier working versions for rollback.

Source ZIP SHA256: `f7061cf27494acf2f9106326123398f25e38222906be112c62e650d9d5a9a7a9`.
Release WASM SHA256: `7fbba846d2817771ee77fd8b229a1a05c3fb8e25e0e424e14de3426d08963b0c`.

Official CLI 3.0.2 / rules 1.0.1 and build are recorded in every result. This
report does not alone claim a live upload; see CURRENT.json and deployment JSON.

Deployment update: uploaded as platform **v89**, submission
`be6416ec-9a15-46cf-9d32-bcb963017ba8`. Server source hash matches; successful
server build and LIVE status are verified. All44 groups /220 games of the next
field curriculum are requested as v89 on35 maps in both seats. The first30
repeat the v88 opponents/maps and score7/30 versus8/30, with zero faults/fuel
losses; Cozy contest deposits rise200 to600 with unchanged800 collection.
Collection/native verification continues; see V89-CURRICULUM.md and CURRENT.json.
