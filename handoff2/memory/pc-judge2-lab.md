---
name: pc-judge2-lab
description: "Local Judge 2 bench on the user's Windows PC (lab\\j2): how to run candidates, speed, gotchas, the user's rule for local feedback"
metadata:
  node_type: memory
  type: project
  originSessionId: c9521f52-ad18-4bf5-bfbc-b8b28ace65cb
  modified: 2026-10-25T12:11:03.021Z
---

Local Judge 2 (from git branch claude/project-thread-til6f5 handoff/judge2) lives in C:\Users\Javier\Cambc2026\lab\j2, using venv C:\Users\Javier\Cambc2026\lab3 (cambc 3.0.5; global cambc stays 2.2.1 for the old GA farm).
- Run: `..\..\lab3\Scripts\python j2run.py <dir|zip|-> NAME --jobs 16 [--near] [--alt 40] [--keep] [--logs RE] [--rivals k_vvl_mgwp]`; queue `j2queue.py`; variants `mkvar.py`; merges `combo.py` (BASE env); `pad.py BOT N` + `diffcount.py` (fuel sensitivity); `h2h.py RIVAL BOTS` (head-to-head); `altcmp.py` (hold-out maps in mapsalt/).
- maps40/ = platform pool renamed. 800 games ~4.8 min with 16 procs.
- Gotchas: never name a script queue.py; project tools from git that test '/A_' in paths need a Windows fix (see ffp/*_win.py); PowerShell pipes mangle binary (use cmd /c git show > file); /mnt/project-files isn't reachable, ask for git handoffs.
- User rule (2026-10-25): local judge is only a prediction, online decides; but every candidate must beat the current bot (kvvl v164 = bots/k_vvl_mgwp) head-to-head (40 maps x 2 sides, near maps reported apart). Report that first.
- Noise lesson: on fuel-dependent bots any code change reshuffles ~96% of games (J2 noise ~9 pts); deterministic fuelfit bases (b29/b32+) change 0-2% with +20 instructions.
