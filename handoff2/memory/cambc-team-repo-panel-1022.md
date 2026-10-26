---
name: cambc-team-repo-panel-1022
description: 10-22 PR #46 on the team repo puts bot v110 (bots/v110, renamed from study27-economy) and the rival panel (panel/run.py, maps_site40) on GitHub for teammates
metadata:
  type: project
---
2026-10-22 07:50 UTC, thread "Base v110 and local testing on GitHub": PR https://github.com/Javiops/Cambridge-Battlecode-2026/pull/46 (branch claude/project-thread-lihebe).
- Current bot folder in the repo is now `bots/v110` (git mv study27-economy -> v102 -> v105 -> v110, one commit each). Next versions: git mv bots/v110 -> bots/v1NN and edit in place ([[cambc-repo-versioning]]).
- Local filter for teammates: `python3 panel/run.py BASE CAND [--rivals ..] [--maps ..] [--gold]` (9 rivals panel/rivals, 40 maps maps_site40, caches out/panel/res by src hash; judge = panel/scripts/judge.py, ex pair6.py). Docs panel/README.md, calibration panel/CALIBRATION.md. Source: [[cambc-local-filter-panel-1021]].
- Cloud setup verified: pip install the 3.0.4 wheel, curl wasi-sdk/cmake/ninja into /root/.cache/cambc, `cambc init --yes` (maps refresh fails, harmless).
