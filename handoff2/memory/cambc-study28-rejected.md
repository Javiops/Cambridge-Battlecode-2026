---
name: cambc-study28-rejected
description: 2026-10-15 the six dissection-driven switches tested on study28 that lost or were noise (P_CHANSTART, P_PACKREACT, P_OPENNUM, P_CASTDIST, P_ROWSEND, P_STACK_HP 2700) with their numbers
metadata:
  type: project
  modified: 2026-10-15T15:36:00.000Z
---

Related: [[cambc-study28-chancancel]] [[cambc-online-ab]]

**Rejected (coin flips vs study27, hold/dev maps both sides):** P_CHANSTART 1 (don't start a doomed tribute) 4-4/22-5 no gain over
cancel alone; P_PACKREACT 6 (regroup/back off before the first hit when a pack outnumbers us) 9-13/24-20; P_OPENNUM 1 (open only with
numbers) 1-1/5-4, almost never fires because P_ENGAGE2 already needs numbers; P_CASTDIST 4 (ranged keep 4+) 2-3/12-12; P_ROWSEND 150
(rows end-game: no shop/free recalls, bank every bag) fires only on the official rows map, 1-1 there; P_STACK_HP 2700 2-5/12-9.
All stay in study28's params.h at 0 with their numbers. Collision's 108-gem elk cluster: choose_target scores it 0.46 vs 11 for the
22-gem camp 4 tiles away (needs 3 champions, ~60 rounds); no per-map rule forced.
