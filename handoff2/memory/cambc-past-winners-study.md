---
name: cambc-past-winners-study
description: Study of past Battlecode winners (MIT 2020-2026, Cambridge spring 2026) with takeaways for our CAMBC bot, saved at /mnt/project-files/analysis/past-winners.md
metadata:
  type: reference
  modified: 2026-10-13T11:50:01.150Z
---

On 2026-10-13 a thread studied past winners; full write-up at
`/mnt/project-files/analysis/past-winners.md`. Key takeaways for [[cambc-bot-project]]:
XSquare-style per-tile fight scoring (github.com/IvanGeffner/battlecode23 MicroAttacker.java),
test against the real ladder with `cambc ladder` / `cambc match unrated <team id>` (Blue Dragon's
scripts, github.com/BenjaminKovacs/Blue-Dragon-2026-Cambridge-Battlecode, needs user's `cambc login`),
copy the top teams' plan from their replays, hunt/protect gem carriers, freeze builds before deadlines.

Access notes: github.com clones work from the cloud; battlecode.org (postmortem PDFs) is blocked by
the proxy and WebFetch cannot resolve it. Spring 2026 Cambridge used a different game (Python, builders).

Follow-up (2026-10-13): deep dive on winners' fight code with C++-portable pseudocode at
`/mnt/project-files/analysis/winners-micro.md` (XSquare BC22/battlecode23 MicroAttacker + MicroSage,
Gone Fishin' focus fire/kite/group, 4 Musketeers run/stand rules, camel_case hit-and-run, SPAARK
weighted scores), mapped to CAMBC reach/cooldown/stun rules.
