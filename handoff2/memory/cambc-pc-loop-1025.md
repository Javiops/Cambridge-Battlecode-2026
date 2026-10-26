---
name: cambc-pc-loop-1025
description: "10-25 online loop rebuilt on the PC in lab\\loop (web endpoints for upload/activate, scripts, timings, chain 21 kvvl ref + b35nohp +11/10.4)"
metadata:
  node_type: memory
  type: project
  originSessionId: 426981f4-a5ba-4438-9d49-0054b9039b2c
  modified: 2026-10-25T18:03:06.666Z
---

Loop online rebuilt 10-25 on the PC in `C:\Users\Javier\Cambc2026\lab\loop\` (README.md = method + endpoints, INFORME.md = results). Only the loop session changes site state (upload/activate/challenge); scripts take `data\send.lock`.
- Upload without `cambc login`: `POST /api/v1/submissions` body = raw zip, content-type application/zip, x-file-name, x-note (from the web JS). New upload is selected; it compiles only when a match needs it (~30 s after the first challenge).
- After `PUT /submissions/active` v164 stays "queued" until a match: post.py sends one kvvl CONTROL replay of the first pinned group (compiles v164 in ~20 s, and checks determinism: 5/5 identical on 10-25).
- Groups finish ~5 s after sending: the limit is the quota (50 groups/rolling hour) -> 3 candidates/hour at 16 groups (15 + control).
- Loop near/far = spawn walk < 60 / >= 60 (mapfeat40 d_spawn); bench cut <35 also reported. cmp_ref reproduced chain 20 exactly (b35 -4, near 44 vs 52/76, far 20 vs 16/44).
- `/submissions` field `pinned` = true after a manual PUT, false after an upload.
- Chain 21 (rivals ranks 57-71, we were 72nd): kvvl v164 ref 33-42 (15:17 Madrid). b35nohp = v175: 44-31, changed 27 (19/8), net +11, bar 10.4 -> passes this one batch; near<60 31 vs 25/49, far 13 vs 8/26, near<35 16 vs 14/23. User decides promotion.
- 10-25 chains c22-c24 (fresh kvvl refs, live ahead15, sides alternate via draw.py --sides alt; c21 was all side a because the site defaults to a): b35nohp TOTAL c21-c24 300 pairs 145-155 vs kvvl 130-170, changed 97 (56/41), net +15, bar 19.7 -> no pass; far 25/9, near<60 31/32, near<35 12/13. Per chain +11, 0, +2, +2. Controls 5/5 identical every chain. series.py chains them; cand.py --version V reuses an uploaded version; cand waits until 16 groups fit before selecting (else the candidate plays ranked while waiting).
Related: [[cambc-online-loop]] [[cambc-chain-tools-1024]] [[cambc-pinned-replay-1019]] [[cambc-coordinator-here-1025]]
