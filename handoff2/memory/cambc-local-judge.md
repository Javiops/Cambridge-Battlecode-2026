---
name: cambc-local-judge
description: "2026-10-16 local judge: calibration (fight changes overstated locally, farming fine), 153-game death analysis (14 deaths/game carrying 81 gems), five specialist opponents (caster panel tracks online 2x better than self-play, now in farm fitness), online quota plan (6 fight maps, rivals 11-30, A/B hourly); PR #29 also fixed 4 gate bugs"
metadata:
  type: project
  modified: 2026-10-16T19:40:00.000Z
---

2026-10-16 14:49 UTC the user wrote in the project chat: since the GA genomes were pushed to main we have not seen the online impact expected after solid local work; online gives at most a few dozen games an hour and locally we overfit to beating our own bot instead of the top teams.

**Why it matters:** it reverses the earlier call to skip point 1 of the plan (fix the judge) in favour of points 2-5 ([[cambc-strategy-1016]]); the farm's champion tournament is only as good as its rival pool.

**Thread:** "A local judge that predicts online", root cmsg_017gbamt2g1g8hMHRHQBc6qbX1fjpEFgMtKJSwjEKyCnKT, branch claude/local-judge-1mgyqy: calibration, specialist panel, quota plan. Never sends online challenges.
**How to apply:** until it delivers, treat local PASSes as weak evidence; the farm's reweighted fitness and leader-persistence rules ([[cambc-ga-farm-tool]]) are the interim guard. Related: [[cambc-local-testing-review]] [[cambc-online-ab]] [[cambc-replay-imitation]] [[cambc-ghost-arena]] [[cambc-dev-speed]] [[cambc-online-loop]].

**15:08 UTC (PR #29):** four gate bugs fixed: gate.py counted unfinished games as splits / faults only on site maps (ab.py dropped FAIL maps); missing spar11/12/16 panel silently skipped; online_base hashed all zip files not just C/C++ sources; online_base took the last versions.jsonl line, not the newest, as the online bot. ga65a6's gate log was clean.
Calibration: none of six changes since 15 Oct decided online (p>=0.38), local called four wins; study28 83% local / 55% online (0.2% chance if real), ga65a6 69% / 57% (5%); farming changes predict fine; ~half of online flips are rivals updating.

**15:40 UTC delivered (PR #29, I070):** online vs top 30 (153 decoded games): we die 14.1/game carrying 81 gems, kill 4.8; top 10 die 2.9; died10 14.9% vs 2.8%; retreat curve close to theirs, so the gap is fight execution. Specialist panel tools/panel (build_panel.sh: sp_castera, sp_casterh, sp_hunt, sp_centre, sp_farm = online zip + switches; P_HUNT in hunt.h): caster ones fit best (our win 53-71% vs 29% online, per-map win corr +0.5, self-play +0.3); none as lethal as the top 10; ranks the last 3 versions in online's direction (ga65a6>economy 63% vs 57% online, self-play 69%) with a home edge for the online code. Weights sent to the farm thread: castera x2, casterh x2, centre x1, hunt x0.5, farm 0. Quota advice: fixed 30 rivals + fixed mapIds, six fight maps (collision, interlock, packs, lanes, elkring, corners), rivals 11-30, ABAB, tie under 57% after 2 h each; eight/contest/pilgrimage almost never flip online, check locally. Report: /mnt/project-files/analysis/local-judge-2026-10-16/README.md. Coordinator sent the plan to the Dissect thread 15:38 (keep ~4 stampede groups while the centre rule is under test).

**19:40 noise floor:** no-op rebuilds of v51 (fuel use only) span 116-124 of the 170 site-map panel games, a pair flips up to 20; a gap under ~10/170 is noise. Adjudication: fixes3 (v52) is the only version ahead of v51 on both the 12:52-built and the v51-built panels (+17 / +6). bots/anti_feed (v50) is in commit 3a2d263.
