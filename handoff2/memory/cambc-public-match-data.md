---
name: cambc-public-match-data
description: All CAMBC match stats and replays are public via the site API (no login); where the 2026-10-13 analysis of why we lose lives
metadata:
  type: reference
  modified: 2026-10-13T12:06:47.779Z
---

Public, no login (2026a.battlecode.co.uk/api/v1): `match-groups?scope=all` (25 per page,
next page `before=<createdAt>_<id>` of the last group), `match-groups/{id}` (every match with
full end-of-game `statistics`: per-champion gems, gold, items bought, kills, damage, draft
picks), `matches/{id}/bundle` (zip with replay.repl26a), `ladder`. The user pointed at
/game/matches?group-scope=all. Draft id order = `champion_draft` enum in the SDK cambc.h
(0 ryth, 1 vesper_vale, 2 vendetta, 3 cassi_and_issac, 4 stellar, 5 prism, 6 marcella,
7 willow, 8 ren, 9 varg, 10 tavi); champion `type` uses `champion_type` (cassi/issac split).

The user's team is very likely "Hidden Tributers" (inferred from replays, not yet confirmed).
Analysis 2026-10-13: `/mnt/project-files/analysis/por-que-perdemos.md`; data in
`analysis/data/rows.json`; scripts in `analysis/tools/`; 283 replays in `analysis/replays/`.

**Why:** a shared student-run server; the user reported a server error during a bulk replay
download (unclear if related), so the download was stopped.
**How to apply:** fetch politely (sequential, delays, back off on 5xx), prefer small samples,
and ask the user before bulk downloads. See [[cambc-site-access]], [[cambc-bot-project]].
