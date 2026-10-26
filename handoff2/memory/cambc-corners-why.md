---
name: cambc-corners-why
description: 2026-10-15 why we lose corners (14-69 vs top 30): lone walk-backs to the held centre, leaving at 35% hp too late; report analysis/corners-why-2026-10-15
metadata:
  type: project
  modified: 2026-10-15T15:59:49.995Z
---

2026-10-15 16:10 UTC study of 160 online corners games (36 decoded, study26/27), report
/mnt/project-files/analysis/corners-why-2026-10-15/README.md (scripts inside).

- Not the draft: vs teams with our exact 5 (Ryth/Stellar/Prism/Ren/Tavi) we are 4-17; mirror games 90 deaths vs 18 with ~equal damage.
- Same damage and ranges as the winner (22.9k vs 22.1k a game in losses), but we die 16.4 vs 4.6, dead 33% of the time vs 9%.
- First centre fight r20-45 at even numbers; we are behind on deaths at r100 in 17/23 losses; then a steady bleed (2% in wipes).
- 35% of our deaths = champion fresh from spawn with <=1 ally within 6 (them 11%); 61% outnumbered by 2+.
- Below 35% hp ours are 3.2 tiles from a foe and 63% die; theirs 5.9 tiles and 70% recall home.
- Code link (inferred): P_HOLD 200 is still on in the caster bundle (since v21): centre camps x2 and ignore danger, flee only at P_UNI_FLEE 35.
- Proposed (not built): return in groups / farm own half, leave at 50-60% hp, P_HOLD off; needs online A/B ([[cambc-online-ab]]). See [[cambc-centre-hold]].
- 16:50 UTC test (test-results.md beside the report): corners-only variant = hold kept + lone champion skips held camp near a pack seen <=16 rounds + leave at 45% (zip bot/mybot_study27_corners.zip): corners panel 16-0, deaths 2.2 vs 3.3, identical elsewhere. Hold off on corners loses the centre locally (0-8 vs study27/casters). Mite rules on other maps (zip mybot_study27_mite.zip): lose 44-135 maps (leave at 50% = -5% farm speed); not recommended.
- 2026-10-15 17:09: the user uploaded and activated study27 + corners fix (mybot_study27_corners.zip) as the live bot. The online loop (thread "Dissect the top 2 teams", [[cambc-online-loop]]) scores batches from 17:46 under that version; 16:40 was the last plain study27 batch. Like-for-like corners comparison vs the 15:39/16:40 study27 batches comes after two batches.
