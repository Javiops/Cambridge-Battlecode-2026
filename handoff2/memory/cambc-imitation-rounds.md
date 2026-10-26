---
name: cambc-imitation-rounds
description: "2026-10-16 imitation rounds 2-4: im_a dies 89 vs casters (online 34), im_p (fight like Mite only with ally within 2) online since 15:20, targeting/recall not gaps, formation gap 59% vs 39%, round 4 pair movement rejected"
metadata:
  type: project
  modified: 2026-10-16T16:24:00.000Z
---

**15:20 UTC round 2 (README "Round 2"):** vs spar11+16 (36 games) im_a retreats like Mite but deaths 89 vs 34 (online bot), wins 32 vs 34 -> self-play gain from beating a passive self. Mite has an ally <=2 on 59% of contact turns vs us 39%; we die alone at 30-50% hp 27% (Mite 20%), paired 8.5%. I062 im_p (Mite thresholds only with ally within 2): gate 38-49 ns, panel 22/11, casters 36/36, deaths 56; zip mybot_ga65a6_mono_fuelguard_jackpot_imitation_paired.zip. Farm pair genes on im_a FAIL (5-19, 4-21, 16-33). I061 nearest-first (P_TGT_DW 400) 16-6 p=0.052 on im_a. Untracked bots in repo bots/ excluded via .git/info/exclude. Thread's pick: im_p. User had uploaded the im_a combo at 15:09; coordinator posted a decision card (swap to im_p) and asked New maps for mybot_online1252_jackgo_imp.zip.

**15:32 UTC round 3 (README "Round 3", PR #28):** correction: "Univardisty picks the gem carrier 84%" counted turns with no carrier; when targets differ in gems we already pick the richest more often (us 60%, Univardisty 51%, Mite 43%), not a gap. Recalls: we recall slightly more, from closer, with fewer gems; Mite also recalls at full hp as a quick way home. Nearest-target on im_p: 14-8 n.s., 36/36 vs casters, 54 deaths but fewer kills (268 vs 285), parked. Remaining gap = formation (ally within 2 on 59% of Mite fight turns vs our 39%). Go-ahead 15:33 to test pair movement between camps, judged on the caster panel and local-judge specialists, not self-play. im_p's ally-within-2 check handed to the farm as a switch.

**Round 4 (16:24 UTC) rejected: pair movement between camps.** Rule: near the middle or in the enemy half, prefer a camp a teammate is heading to, never go alone; 4 variants. Always-on variants cut deaths vs the caster bots (43 and 40 vs im_p 56) but farm 7% slower and lose 1-16 / 2-18 to im_p; enemy-triggered variants keep speed but deaths stay 59-62. All four win fewer games vs the caster bots than im_p (31-33 of 36 vs 36). Locally an ally is within 2 tiles ~50% of fight turns already; the 39% online comes from how real opponents split us, not camp choice. Goes on the rejected list with team-ball and trio ([[cambc-group-fight]]). README "Round 4". im_p stays online.

Related: [[cambc-replay-imitation]] [[cambc-online-versions-1016]] [[cambc-ga-farm-tool]] [[cambc-local-judge]].
