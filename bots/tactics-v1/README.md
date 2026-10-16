# Tactics v1 — draft implementation

This is a modular implementation of the team's tactics handbook at
`20c97a701bc9ddb45a23951e6ea28a79f7f22df9`. **It is not ready to replace the live
bot.** Frozen integration15 loses all28 development games. It completes them
with zero candidate native faults, caught/API errors or fuel exhaustion. The
final18-game holdout remains unopened.

## Responsibilities

Observation and immutable geometry live in sdk_world.h/geometry.h. actions.h
is the sole mutation gateway. main.cpp/coordinator.h own the epoch, budget,
mission and channel lifecycle. economy.h/cycles.h handle farm, capture, bank,
recovery and common-endpoint comparisons. resource.h separates completed score
from unpriced gold fallback. solo.h/solo_bounds.h, squads.h, coordination.h and
assembly.h separate actual contribution, bounded forecasts and future intentions.
combat.h/deny.h own legal exchanges, control, protection and escape.
vision.h/strategic.h/information.h handle mission observation, bounded exits
and the eight-byte advisory protocol. shopping.h verifies private budgets,
exact bundles and named completed-gem investment continuations. draft.h retains
the declared initial geometry-based recipe. ranking.h/log.h bound ranking and
decision records.

No map-name or signature strategy branch is used. Personal visibility, actual
HP/permissions and observed completion remain distinct from estimates and claims.
The two spells share one cast allowance. A channel start is not banked score.

## Repairs in this checkpoint

- Keep the actual surviving camp target for next-owner route preparation.
- Cache immutable camp metadata/coarse geometry; keep dynamic facts fresh.
- Preserve funded action/refresh reserves and reject old epochs after suspension.
- Execute certified reset/basic through a one-use receipt, with fresh native
  permission and unchanged participant checks before the sole mutation gateway.
- Compare altar endpoints, alternative safe channel tiles and failed approaches.
- Price an actual affordable purchase through a named gem clear/capture/bank/
  recovery cycle, and restore its mission only after a verified real purchase.
- Prevent ordinary gold-only farming from inventing completed-bank value; keep
  actual holders and a separately valued monolith-only growth fallback.

## Current limits and next repairs

All28 benchmark losses remain visible. A current caller incorrectly supplies
self DPS before reaching an actual contribution tile. Internal generic rollout
work can also exceed its nominal slice; both are being repaired before tuning.
Zero-wallet gold-first investment, spell-only solo staging and full autonomous
rendezvous activation remain bounded coverage gaps. The source audit is not a
claim that all96 tactical topics are complete or verified. Optional teleport and
owned-lock strategy, global partitions and fitted counterdrafts remain deferred.

## Reproduce

Use official CLI/SDK2.2.2 and engine0.0.2. On Windows generate the normal compile
database before the release build:

```sh
cambc build bots/tactics-v1
cambc build bots/tactics-v1 --release
```

See validation/checkpoint15.json for exact source/module/runtime identities,
all results and known issues. tools/tactics-v1-validation contains scoped
production-helper tests and native fixtures. A future submission ZIP must place
src/main.cpp and its headers directly under the root src/ directory; this
checkpoint is a review artifact, not a promotion ZIP.
