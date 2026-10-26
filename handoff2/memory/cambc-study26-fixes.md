---
name: cambc-study26-fixes
description: 2026-10-15 the user's 6-item fix list on study25 -> study26 (dash Issac, reset check everywhere, AoE aim); what lost (cast-or-escape) and PR #3
metadata:
  type: project
  modified: 2026-10-15T11:55:00.000Z
---

11:05 UTC 2026-10-15. study26 = study25 + P_DASHFIX 1 (enemy Issac dashes, not Cassi) + P_U34_RESET_LIVE 2 (reset
alive-check on every map) + P_AOE 2 (Stellar area spell aims at most foes, cast first with 2+ under it).
Team repo PR #3 (bots/study26, docs/study26-fixes.md); zip bot/mybot_study26.zip. Not uploaded; user decides.
Results vs study25 on 313 maps (official+gen+hold60+dev200, maps won/lost both sides): study26 50/40 (p 0.34);
dash 32/28, reset 25/16, AOE2 19/12, AOE1 14/7. Panel 48-6 (study25 47-7) but more deaths (191 vs 153).
**Rejected:** P_CASTSAFE (skip rooting casts when we should escape) 12/29 at 70%, hp-only 15/30: standing to cast
beats escaping, again. P_R5_WARD 55/58 (noise, 2nd time). P_KITEFRONT 1 (front before kite) 17/13, 2 = 5/5.
Related: [[cambc-teammate-bot]] [[cambc-eval-method]] [[cambc-danger-level]]

**Lineage update (2026-10-15 UTC):**
- study25 = study24 + `#define P_CAPRECALL 2` (recall starts on the capture tiles on every map when hurt, wanting
  to shop, or 90+ gold). The user's idea. vs study24: 16/6 maps-both-sides on gen, 19/13 on hold60; 88-34 vs v30 on
  200 new maps. Team repo Javiops/Cambridge-Battlecode-2026 bots/study25, PR #1 merged by the user; zip bot/mybot_study25.zip.
- study26 (above) = study25 + the 3 fixes; PR #3 merged 11:13 UTC at the user's request ("commit the changes over the
  current version in gh"). Edge 50 vs 40 is small/unproven. Not uploaded to the site as far as known (v34 = study24 live at 08:53).
- Rejected on study25: danger level P_DLEVEL (all variants); Mite's draft/recall-banking/damage-cost card rules
  (bot-st25-card/src); stacking champions per camp as a general rule (rows 436->392 rounds but expanse slower, net
  noise over 213 maps); mite_s25 (Mite shop+fight rules, equal to study25); mite_scratch (15% win rate).
- Testing: `python3 tools/ab.py bots/CANDIDATE bots/BASE` with CAMBC_WASMTIME_CACHE (PR #2 from the "Faster measuring"
  thread, merged by the user), 4x faster; ~150 decided maps needed for a real edge. See [[cambc-ab-tool]] [[cambc-top1-cycle]] [[cambc-mite-bots]].
2026-10-15 11:32 UTC: user says site version 35 is now active; 11:55 UTC the user confirmed the current site version (v35) is study26.
2026-10-15 11:36 UTC study26_stack (bot/mybot_study26_stack.zip, from the cycle thread; report analysis/top1-cycle-2026-10-15/stack-or-spread.md): up to 4 champions on camps of 3000+ hp (2-3 elks, elk+wolves, 3 wolves), one on smaller camps; vs study26 154 maps won both sides / 106 lost (p<0.01) on every set incl. 150 maps made after tuning. Pairing on small camps loses; map-level features don't predict stacking. Idle check: our champions waste 2-5% of steps like Mite; standing = waiting for a respawn, moving them off lost. PR as study27 requested.
11:53 UTC: P_SYM-style mirrored tie-breaks on study27 lose 107/212 maps vs study27 and farm ~4% slower (side-B fuel overrun on rows); side doesn't matter on average (33/20 vs 21/32 as A/B). Leave as is.
2026-10-15 12:08 UTC: PR #4 (study27 = study26 edited in place: P_MAX_SHARE 4, P_SHAREEXP 75, P_STACK_HP 3000; body has a Spanish handoff study24->study27) merged by the user; study27 uploaded and ACTIVE on the site (version number not yet given; v35 = study26 before it). Online loop compares it with v35.
- 2026-10-15 12:40 online (unranked loop vs top 30, 155 games): study27 58-97 (37%) vs study26 59-91 (39%); like-for-like on 77 shared opponent-map pairings 24 vs 25 wins = noise. The stacking change (P_MAX_SHARE 4 / P_SHAREEXP 75 / P_STACK_HP 3000) did not move results online; rows still 18%, lanes 3-14, packs 6-16, monolith 5-11; elkring/expanse/interlock roughly even. Numbers: /mnt/project-files/online/data/hourly.md.
