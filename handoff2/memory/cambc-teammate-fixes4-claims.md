---
name: cambc-teammate-fixes4-claims
description: 2026-10-16 ~21:30 final round on v52 (claim reassignment P_CLAIMCLR, corrected P_CAMPBAIL 3, roster fuel fix, P_CARRY): nothing clears the two-panel bar, v52 stays; switches committed on PR #31
metadata:
  type: project
  modified: 2026-10-16T21:30:00.000Z
---

Follows [[cambc-teammate-fixes3-cases]]. Switches are in bots/teammate_fixes (commit 5f4cbdd, PR #31); all default 0 = v52. Flips won-lost vs base, panel v51 / panel 12:52 ([[cambc-panel-noise]]):
- Roster fuel fix (P_ROSTER 1 + P_OCMEMO 1, from [[cambc-micro-tracking]]) vs v52: 4-7 / 8-11, no gain.
- P_CLAIMCLR (user 20:19: claim at kill time goes to the nearest free ally, DPS first, re-evaluated if claimant dies/recalls/leaves): mode 1 (only orphaned claims) 21-11 / 14-26 split; mode 3 (full re-claim) 15-22 / 14-24 worse, farms slower.
- P_CAMPBAIL 3 (bail when hp < 3 rounds of all camps in range): wins noise (8-4 / 2-5) but deaths -0.46 / -0.39 per game (t -1.9 / -2.3), the only consistent death cut; farm unchanged.
- P_CARRY 20 (Varg on eight): 18-6 / 8-13 split.
Fuel trap: a roster or champions() call inside choose_target/count_claimers raises the P_FUELGUARD ct_cost forever -> permanent fuel-wait (gems/100r fell to ~40). Read allies once per round (away_bits) and is_recalling only via vision.
**How to apply:** v52 stays online; CAMPBAIL 3 is the candidate if the user wants fewer deaths at no win cost.
