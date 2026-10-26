---
name: cambc-local-testing-review
description: 2026-10-16 08:36 review of local testing: 0 of 8 local fight wins held online, gate power 12% at 260 maps, base not verified vs online bot, 17 online maps vs 9 local; 6 proposed changes, user to pick
metadata:
  type: project
---

2026-10-16 08:27 UTC the user asked to review how we test locally; thread "Revisión del testeo local" reported at 08:36 (no tools changed yet):
- Fight: of 8 fight rules that won locally, none won clearly online. The only local signals that held: the caster panel used as a veto, and Fran's confirmation on 512 fresh maps with a frozen bot.
- Farm: mechanisms are visible in replays, but +1-3% gems does not flip games we lose by dying.
- Gate power is low: with 260 maps a real 55% improvement passes only 12% of the time, so threads add maps or try levels until one passes (how RecallCost and P_RECALL_PCT 50 "passed").
- Wrong base: gate.py compares against main and nothing checks main is the online bot (today's study27-economy mismatch; the overnight "corners fix 66 vs 64" may have compared a different bot, depends on when study27-economy went live).
- Maps: the site now has 17 maps, local sets have the 9 official; today's three worst (contest 1-43, eight 4-38, stampede 6-31) are in no local set.
Proposed changes, in order: (1) base = the online bot, verified by zip hash (~1 h); (2) local set with the 17 site maps (~1 h); (3) verdict on a fixed 600-1000 fresh maps per idea, never extended afterwards (~5 CPU-min; a 60% improvement passes 93% instead of 38%); (4) do not upload farm gains below 58-60%; (5) measure against a rival pool, not only the base; (6) check whether the caster panel ranks old versions as online did.
**How to apply:** until the user picks, treat local PASSes obtained by extending the map set as unreliable; new ideas should be judged with a fixed pre-declared map count. Related: [[cambc-eval-method]] [[cambc-harness]] [[cambc-online-ab]] [[cambc-online-is-economy]] [[cambc-new-maps-1016]]
**09:05 UTC follow-up (user "ok continua", items 1-2 done):** PR #20 (branch claude/local-testing-review-elhlmb): online/version.py --zip,
tools/online_base.py, `gate.py X online`, site-map line in gate phase 1, ab.load_stats for cambc 2.2.0 (stats binary unless --json;
engine 0.0.2; `cambc init` now pulls all 17 site maps; `--release` build fails on our bots). versions.jsonl records study27-economy
with zip /mnt/project-files/bot/mybot_study27_economy.zip (src 1c86702e07). **Bug: on `contest` our bot scores 0 gems** (only gem
source is one 200-gem monolith; the bot skips monoliths -> farm=no-target); online 1-43, mostly 0-0 at r2000. Not fixed yet.
**09:50 UTC:** the caster panel no longer separates versions near the online bot (economy beats spar11/12/16 both sides 67-8, 85-4, 65-9 on 100 fresh maps, GA thread); the gate panel veto is near-powerless; the rival pool should include rivals that still beat us (GA best genomes).
