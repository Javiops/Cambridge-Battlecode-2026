---
name: cambc-less-reporting-1025
description: USER 10-25 ~21:35 - stop relaying every session update; the coordinator runs the work autonomously and reports only when the user asks or a real decision/result needs them
metadata:
  type: feedback
---
USER 2026-10-25 ~21:35 Madrid: "no me comentes tanto, todo tuyo, te encargas tú, ya te pediré feedback si lo necesito".

USER 2026-10-26 ~01:40: "no digas sigo, no hace falta en cada mensaje, solo sigue trabajando" → when a session message needs no user-facing news, reply with nothing (no "Sigo").

**Why:** the coordinator was relaying every session message to the user.

**How to apply:** handle session messages silently (act on them, steer the lines). Write to the user only for: an online verdict of a candidate (pass/fail vs the 15 ahead), a promotion decision that needs their words, something broken that needs them (cookie, PC, limits), or when they ask. Keep those short. Standing rules still apply (Spanish, Madrid time from the PC clock, only confirmed facts). Related [[cambc-coordinator-here-1025]], [[cambc-plan-c97-1025]].
