---
name: cambc-bundles-loop-only-1026
description: "Coordinator rule 10-26: only the online loop downloads replay bundles; other sessions ask it; API summaries are fine"
metadata:
  node_type: memory
  type: project
  originSessionId: 1b4bd233-3231-42db-8273-34243c84379e
  modified: 2026-10-26T00:37:38.055Z
---

Since 2026-10-26 (coordinator): the site prepares only one replay bundle at a time per account and that blocks the loop. ONLY the loop ("Loop online en el PC [ac7f2a]") downloads bundles; any other session that needs one asks the loop. Match summaries via API may still be requested by anyone.

**Why:** concurrent bundle requests stall the online loop.
**How to apply:** never fetch bundles from peleas/farmeo/top10 sessions; send the loop a request instead. Related: [[cambc-cookie-shared-1025]].
