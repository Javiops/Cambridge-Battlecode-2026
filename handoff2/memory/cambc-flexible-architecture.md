---
name: cambc-flexible-architecture
description: 2026-10-16 18:06 user principle (from an MIT Battlecode finalist): strong flexible architecture early, never lock into one strategy, so the bot can adapt to the meta in the final days before 3 Nov
metadata:
  type: feedback
---

2026-10-16 18:06 UTC the user wrote: "focus on strong architecture at the start and decisions that make your strategy very flexible, so that you can adapt to the meta in the final points of the competition ... you just don't want to pigeonhole yourself into any one strategy too much; this is the advice an MIT Battlecode finalist winner told me."
**Why:** the competition ends 3 November 2026 ([[cambc-deadline]]) and qualifying maps are new ([[cambc-new-maps-rule]]); the meta (caster drafts, centre holds, farm routes) shifts, and today's experience (GA, imitation) showed point fixes that overfit.
**How to apply:** every structural change (farming by roles rebuild in [[cambc-teammate-fixes]], draft, fight doctrine, camp selection) should be a swappable module or profile selected by map features and P_* switches, with strategy as data (tables/params) rather than scattered conditions, so a late meta change is a parameter edit, not a rewrite. Keep the switch-off-equals-base property (identical games with all switches off) so any module can be reverted. Related: [[cambc-harness]] [[cambc-unseen-maps]] [[cambc-micro-strategy]].
