---
name: cambc-coordinator-here-1025
description: USER 10-25 (new account) - the coordinator that decides what gets investigated now runs in the Claude desktop app on the PC, not in a claude.ai Project
metadata:
  type: feedback
---
USER 2026-10-25 (~14:20 Madrid, new account): asked where the coordinator should live and chose "Aquí, en esta app" over recreating the claude.ai Project. Before (old account) a claude.ai Project chat coordinated cloud threads and relayed messages (the "integrador"/coordinator notes in handoff/threads/).

**Why:** the old Project does not travel between accounts; the PC already has the Judge 2 bench (lab\j2), the repo and the archive.

**How to apply:** the Claude Code desktop session working in C:\Users\Javier\Cambc2026 is the coordinator: it decides which lines are investigated or closed, opens one session per line on the PC (start_session), relays only what a session's latest report confirms (with Madrid time), and keeps the PC bench in ONE queue (16 cores; two 800-game queues slow each other). Lines started 25-10 ~14:45 Madrid (SendMessage addresses are the session TITLE plus ref, not the short name): coordinator "Battlecode Cambridge 2026 [fcd25f]", "Banco del PC (Juez 2) [cbb5f6]", "Loop online en el PC [ac7f2a]", "Evaluador de nuestras partidas [8fd3fc]", "Análisis del top 10 [eb2fca]", "Peleas sobre la base determinista [08703d]", "Farmeo y macro sobre la base determinista [0a6ad1]". Work folders lab\loop, lab\eval, lab\top10, lab\peleas, lab\farmeo; bench owns lab\j2. Not here: the cloud project folder /mnt/project-files (online/ loop scripts, bundles/, online data) and the site cookie; the online loop needs both rebuilt/provided on the PC. Handoff clone: C:\Users\Javier\Cambc2026\thread (branch claude/project-thread-880vzg); C:\Users\Javier\Cambc2026\repo belongs to the old GA farm, do not switch its branch. Related [[cambc-online-loop]], [[pc-judge2-lab]].
