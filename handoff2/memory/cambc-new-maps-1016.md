---
name: cambc-new-maps-1016
description: 2026-10-16 03:40 UTC the competition site added three new maps (stampede, pilgrimage, ambush), now 12 maps; first results and where the replays are
metadata:
  type: project
  modified: 2026-10-16T14:56:30.817Z
---

On 2026-10-16 around 03:40 UTC the site added three new maps: **stampede**, **pilgrimage** and **ambush** (12 maps in total now). Reported by the "Dissect the top 2 teams" thread, which runs the online challenge loop.

First games (bot online = study27 + corners fix, v36 line): stampede lost 180-1260 and pilgrimage lost 816-1052 against a rank-69 opponent; ambush won in ranked. Replays saved under `/mnt/project-files/online/data/newmaps` so the maps can be extracted for the local arena (see [[cambc-arena-setup]]). From that time the hourly challenge batches also draw these maps.

Overnight online results otherwise unchanged: like-for-like vs plain study27, 66 vs 64 on 179 pairings; ranked 169-151.

**Why:** the user's rule is that strategy must be computed from the map, not hardcoded per map ([[cambc-new-maps-rule]], [[cambc-unseen-maps]]); these three are the first real unseen maps and the first evidence of how the bot does on them.
**How to apply:** extract the three maps into the arena and add them to the A/B map sets; look at the stampede loss first (the margin is the largest). Related: [[cambc-online-loop]].
08:36 UTC update: the site now lists 17 maps (also contest and eight, where we are 1-43 and 4-38); stampede is 6-31 cumulative.
2026-10-16 12:00 UTC: new-maps study done (120 top-10 replays + 48 ours on the 8 new maps). Winners draft Cassi&Issac in all 14 maps looked at and almost always Stellar; winners end with 2x the loser's gold and shop 17-22 times vs our 9-12. Stampede/contest: they farm ~9000 gold and ~50 purchases and take the central group at round 350-475; we go at round 53 and die 27 times per game. Eight: spawn_path 46 vs our caster-draft threshold 45. Fragment/swirl lost by dying (17-18 deaths vs 7-9), same draft. New rule P_JACKPOT 350 (I042): if one group holds half or more of the map's gems and is equidistant from both spawns, gold and shopping first, group from round 350; gate pass 33-31, wins stampede both sides, fires only on stampede of the 17 maps. Zip mybot_ga65a6_mono_jackpot.zip (ga65a6 + P_MONO + P_JACKPOT); 12:03 UTC combined zip exists: /mnt/project-files/bot/mybot_ga65a6_mono_fuelguard_jackpot.zip = ga65a6 + P_MONO + P_FUELGUARD + P_JACKPOT 350, identical (--fuel 100000000, 17 maps both sides) to the jackpot zip 17/17 and to the fuelguard zip 16/17 (stampede differs by design); recommended next upload, not uploaded as of 12:03. Ideas in tracker on PR #26 branch: I040 C&I+Stellar draft everywhere FAIL 37-57 locally, I043 eight spawn_path 46 vs threshold 45, I044 shop cadence 17-22 vs 9-12.

**14:55 UTC online check of the 12:52 upload (34 stampede/contest games since 12:53, tables+replays in /mnt/project-files/analysis/new-maps-2026-10-16/online-check/):** the fixes are active (jackpot rule: no centre before r350, gold 6240 vs Mite 4230; monoliths farmed). Losses are all vs top-24 teams, wins vs unranked. Stampede 0-10 vs top: we die 5-21 times before r500 while farming (they 0-3); they take the centre r305-650 with 2-6 champions, we have 0-1 there, they chain 3 captures (+1080 at r740-1040). Contest 0-7 vs top: deaths from r30-40, ~19 before r500, 64-92/game vs 4-28, a third of their gold; vs Mite/VeryGood 0-0 captures and we lose on tiebreak. Coordinator asked the thread to build a stampede macro rule (whole team to the centre from ~r350, trigger round and champion count as params, switch + identical-games check, zip = online bot + rule only) and passed the death numbers to the local-judge thread (an early camp-hunter specialist is the priority).
