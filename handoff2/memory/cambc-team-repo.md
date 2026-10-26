---
name: cambc-team-repo
description: the user's GitHub repo Javiops/Cambridge-Battlecode-2026 for their friends; what goes in it and the push status
metadata:
  type: reference
  modified: 2026-10-15T11:56:00.000Z
---

17:52 UTC 2026-10-14 the user created https://github.com/Javiops/Cambridge-Battlecode-2026 so friends can start
working, and asked for the latest version in it. Layout (a cambc workspace, Spanish README): bots/v30 (= study22),
bots/spar11/12/16 (sparring), tools/arena.py, tools/variante.sh (copy a bot + params.h defines + build),
maps_gen/ (44 generated maps); official maps/sdk/cmake come from `cambc init --yes` (gitignored).
Tested: init + build + arena + variante.sh work from a fresh copy.
18:02 UTC pushed to main (commit 83dc33f, 60 files; the repo was empty). Saved to the project repo list.
Zip copy: /mnt/project-files/repo/Cambridge-Battlecode-2026.zip.
Never commit the cambc login token. Related: [[cambc-bot-project]] [[cambc-corners-long]]

**2026-10-15 11:56 UTC feedback:** the user said 'i dont want the github to just be commiting new bots'; a PR must change the existing bot in place so the diff shows what changed (e.g. study27 = edits on top of bots/study26, not a new bots/study27 copy). **Why:** PRs #1/#3/#4 each added a whole new bots/studyNN directory, so the diff was a full copy and unreadable. **How to apply:** one bot directory that evolves (the current one on main), each PR = the switch/fix diff + a short doc of how it works and the maps-both-sides results; version zips can still go to /mnt/project-files/bot. PR #4 (study27) is being reworked this way.
