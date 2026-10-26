---
name: cambc-method-ficha-1023
description: USER RULE 10-23 09:09 UTC: every candidate must follow the mechanism-sheet method (§3 of analysis/process-audit-1023/README.md) before panel/online
metadata:
  type: feedback
  modified: 2026-10-23T09:09:58.432Z
---
User (09:09 UTC 10-23): "aplica el metodo a todos los hilos". The method in /mnt/project-files/analysis/process-audit-1023/README.md §3 is mandatory for every candidate:
1. Hypothesis with causal chain and number (rule moves M by X; M moves wins because <online datum>); no datum, no build.
2. Exposure: decisions changed per game, rounds, following states. <1% of decisions = rider inside another candidate, never its own batch.
3. Interaction list before coding (flee/kite/recall/sweep; gold->shop->power; any new fuel reserve breaks all fuel_ok()).
4. Counter in the status line: every new rule prints when it fires and log_status sums firings.
5. Mechanism test, 80 games vs pHuntF before panel: M moves as predicted AND 6 side indicators don't worsen: gold@400, deaths, Vesper deaths, fuel run-outs, first 20+ capture, clears@400.
6. Power: never close a line on <300 paired games ("unresolved" instead).
7. Online: mandatory control subset where the rule doesn't act; expected effect <+6/120 -> stack, judge over 2-3 batches.
8. Stack only after a joint test vs pHuntF.
**Why:** audit showed candidates reached online without mechanism checks (cutguard froze Vesper on big_world; shootfirst raised Vesper deaths).
**How to apply:** write the sheet before building; don't stack cutguard (Vesper freeze bug on big_world).
Related: [[cambc-idle-wallmaps-1023]]
