---
name: cambc-repo-versioning
description: how new bot versions go into the team GitHub repo: edit the current bot folder in place (rename), never add a fresh copy, so the PR diff shows the change
metadata:
  type: feedback
  modified: 2026-10-15T11:57:57.451Z
---

2026-10-15 11:56 UTC the user: "from now on i want to be clear i dont want the github to just be commiting new bots ...
build bot study27 on top of study26 so that i can see what diffed".
**Rule:** a new version in Javiops/Cambridge-Battlecode-2026 is a change to the current bot folder, not a new copy.
Do `git mv bots/studyN bots/studyN+1` and edit the files in the same PR, so GitHub shows a rename plus only the changed
lines. The old version stays in git history (and its zip in /mnt/project-files/bot/).
**Why:** PR #1 (study25) and PR #3 (study26) added whole bot copies (4000+ lines each), so nobody could see what changed.
**How to apply:** every thread that ships a bot version to the repo. PR #4 (study27) was redone this way: study26 ->
study27 rename, 9 lines in main.cpp + 3 in params.h. Related: [[cambc-team-repo]] [[cambc-stack-or-spread]]
