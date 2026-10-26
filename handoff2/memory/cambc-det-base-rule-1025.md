---
name: cambc-det-base-rule-1025
description: USER 10-25 10:17 UTC - ALL threads work on the deterministic base (b32 fuelfit), not only the fuelfit thread; where it lives and the rules for pieces on it
metadata:
  type: feedback
  modified: 2026-10-25T10:20:00.000Z
---
USER 10-25 10:17 UTC: "que el resto de hilos trabajen con la version determinista tambien no solo propongas fixes tu".
**Why:** kvvl/V20 reshuffle 96% of games on any recompile (fuel gates), so pieces measured on them are noise; the deterministic base (pad +20 ~0-1%) makes every measured piece meaningful.
**How to apply:** every thread builds and measures its pieces ON the deterministic base: b32 = branch claude/project-thread-jeb4pf handoff/fuelfit/fuelfit-b32.zip (sha in SHA256SUMS; sources = kvvl/src + applyopts.sh handoff/fuelfit/opts/). Local bench vs b32, probe +20 (ws/sub.sh NAME NAMEq, divloc.py) = 0 changed games, PC J2 vs b32. Piece rules: no fuel reads (fuel_ok is a stub), no new work in the start-up turn (turn 1 is at the 200k cap on many maps, see [[cambc-fuelfit-state-1025]]), no BFS at r2 on big maps, heavy work in fixed rounds. Coordinator relays this to all threads (champ, farm, buddy, PC, API, far, top10, loop). Related [[cambc-fuelfit-1025]].
