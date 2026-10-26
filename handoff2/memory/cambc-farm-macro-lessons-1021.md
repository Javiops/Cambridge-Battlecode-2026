---
name: cambc-farm-macro-lessons-1021
description: Farm thread lessons and closed lines moved out of [[cambc-farm-macro-1021]] on 10-23 (coordination layers, engine limits, closed lines, far-map autopsy, idlerush detail)
metadata:
  type: project
  modified: 2026-10-23T11:45:00Z
---
LESSONS moved from the state file 10-23:
- Coordination layers (orch-v1..v14, recruit/pull, joincall) are flat or lose vs the greedy per-champion value/rounds chooser; the few
  wins came from making squads of 2 feasible (need2 = P_NEED_CAP 2, now in base) and soloelk (P_NEED_SOLO 200).
- Engine: 6 isolated wasm VMs (draft + 5 champions), 8 shared bytes; fuel 100k instr/turn, farm() has 40-50k; planners <15k/turn.
- TONIGHT AUTOPSY 07:15 UTC 10-23 (RESULTS.md 07:15): near maps lose FIGHTS (deaths 16.4 vs 4.8); far maps lose the GEM RACE at
  equal deaths (698 vs 1072 gems, first big capture r360 vs r190, wait-respawn 15% of our champion time in losses vs 10% in wins).
- CLOSED LINES: territory plans (plan-v1..v3, -40..-71 panel17), holdcamp, respwait, recruiting, needed-count below 2, gem-first on
  near maps, blanket rush.
- Online noise: one 120-pair batch cannot resolve 0.7 deaths or 50 gold (~9% pairs flip).
- FAR-MAP AUTOPSY 03:50 UTC 10-23 (analysis/farm-route-1021/online-far/ scripts, RESULTS.md 03:50): v122 far 36% online; in losses we
  clear MORE camps with MORE gold@r400 but half the gems; rival's first 20+ gem capture r182 vs ours r343 with ~3 champions, no kiting.
  Cause: value/rounds prices big elk groups for a pair, gold_w 1.0 until r940. LOCAL RIVALS take big camps at r412 and die 12/g =>
  local far-map farm judging is invalid. bigrush-v1..v6 (blanket trio rush) CLOSED: capture r90 but gold400 -4..-31%, deaths up.
  bundles/rRush1.zip (= rush2) given to the local filter as a far-map mechanism rival.
- idlerush-v1 (bots/idle1, diff orch/idlerush-v1.diff): a champion standing 12+ rounds at a small respawn goes to a 20+ gem group
  priced for a trio. Mechanism moves (first big capture -60..-75 r, far gems@r400 +15%), gates pass vs pHuntF/rFarm1, but panel17
  -5 (bar +80 rule): far mechanism is invisible locally. USER 08:35 UTC 10-23: "pues aparcalo" -> SHELVED, not sent online. idle2 (6 rounds) fails gates.
