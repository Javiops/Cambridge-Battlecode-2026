---
name: cambc-coordinator-updates
description: 2026-10-15 the user wants the Coordinator to keep a running summary of the day's big wins and the bot lineage, posted on request; 2026-10-16 also ping in the project chat whenever a result lands
metadata:
  type: feedback
  modified: 2026-10-16T14:08:38.224Z
---

2026-10-15 11:50 UTC the user said: "I need a coordinator that keeps up with the different big wins that we have had today just to clear my head".

**Why:** many threads run in parallel (danger level, cycle study, audit, dissection, fix list, online loop) and the user loses track of which version is live, which PRs are open and which ideas were rejected.
**How to apply:** when the user asks for an update, post one project-chat message: bot lineage with site versions and PRs (e.g. study24 = v34, study25 PR #1, study26 PR #3 = v35, study27 PR #4), wins that held up with their maps-both-sides numbers and thread links, understanding gained, rejected ideas, what is running. Keep the lineage line in cambc-study26-fixes / cambc-eval-method current so a new coordinator can answer in one message. Related: [[cambc-understand-first]] [[cambc-eval-method]].

**2026-10-16 14:08 UTC:** the user said "ping me when there are some results". So besides on-request summaries, the coordinator posts one short project-chat line whenever a result lands (a champion tournament, an online paired comparison, a gate pass/fail, a rejected track), with the thread linked; silence otherwise. A send_later check-in is armed for 14:52 UTC to post the 14:10 champion tournament and the 14:46 online batch if the threads have not surfaced them.
