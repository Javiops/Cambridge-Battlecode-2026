---
name: cambc-user-prefs
description: The CAMBC user writes in Spanish, is a competitive programmer learning the bc:: game API and bot codebase, since 2026-10-14 builds their own bot from scratch, and wants repo docs in English
metadata:
  type: user
  modified: 2026-10-23T08:40:00Z
---

Owner (display name "Hi, I am having a lot of problems in my coding"), writes Spanish: reply in Spanish. Competitive programmer
(C++ ok; new to the bc:: API, P_* preprocessor switches and this codebase); builds his own bot too; runs the cambc CLI on Windows,
online tests by uploading to the site. Skip programming basics. SDK header copy: docs/ejercicios/cambc.h (bc = namespace cambc).

Related: [[cambc-bot-project]].

2026-10-15 11:56 UTC: "i dont want the github to just be commiting new bots": a PR must edit the existing bot in place (e.g. study27 on top of study26 as a diff), never add a new bots/studyNN copy. **How to apply:** branch from the current bot folder, change files in place, so the PR diff shows only what changed.

**2026-10-15 22:05 UTC:** when the harness thread delivered the development pipeline docs in Spanish, the user said "draft it in english". **Why:** the team repo (Javiops/Cambridge-Battlecode-2026) is shared with teammates, so docs and tooling that live in the repo should be in English. **How to apply:** chat replies to the user stay in Spanish; README, pipeline docs, trackers and code comments committed to the repo go in English unless the user says otherwise. Related: [[cambc-team-repo]].

10-18 13:08 UTC: the user reads times in Madrid time (UTC+2 in October); always give Madrid time with UTC in brackets, e.g. 14:46 (12:46 UTC), or batches get confused.

10-19 08:46-10:12 UTC (audit + API threads, cmsg_017gbamt2g1g8hMHRHQBc6qbXWdJ6RSDd5YSnDV93VGsbW): NO SINGLE-RULE PATCHES. "why are we expecting a sudden +30 improvement over a rule, the whole system is flawed, we have to pinpoint the main issue". **Why:** 12+ one-rule candidates since 10-18 (escape, getout, chase...) moved nothing. **How to apply:** no candidate (and no audit green-light) until a whole-system diagnosis from the top-bot study names the main issue with a decomposition that adds up; then redesign that system as one build. See [[cambc-death-root-cause-1019]].
10-19 23:52 UTC USER STANDING ORDER (API thread, cmsg_017gbamt2g1g8hMHRHQBc6qbLikRpzUsXJrvgswTDwJ5oQ): "keep this loop going: review -> correct focusing on the deeper reason -> propose fix, run them, then batch against 71-95 again". API thread cycles decode -> root cause -> candidate -> local filter -> loop (pinned fresh v76 draw, ranks 71-95, two-step judge) without asking each time.
- 10-20 16:37-16:42 UTC USER: loop rivals = ladder ranks 101-125, re-read from the live ladder at every fresh base draw (~every 2 batches); pinned replays keep their draw (same maps, rival versions, side a). Old 71-95 draw 145753Z replays finish as they are.
- 10-20 16:49 USER: wants rules more general than fixing a single map; next candidates come from all-map data (map-feature fixes like sealed ride as bug fixes, not candidates).

- 10-23 08:34 UTC USER (angry about method): "after analysing our games we find nothing to improve: something deep escapes us, or we fail to put ideas in correctly and to predict how a rule interacts with the rest of the bot; we must beat both obstacles". Said NO to a solo online batch for waitwalk-v2 (rides inside the next candidate). Farm thread answer: (1) decision-exposure tracer (candidate also computes the base decision, counts changed decisions per game/map/round and the rules fired after) before any 800-game run; (2) champion time-budget us vs top-10 in the same online games from full replays. Every thread should state a rule's expected exposure + interactions BEFORE testing it.
