---
name: cambc-panel-noise
description: 2026-10-16 19:35 local judge adjudication: site-map panel noise floor ~10 of 170 games (fuel shifts 4-8, specialists share code with their build base); v52 = fixes3 beats v51 on both panels, fixes2 switches on one only, draft rule +3/+4
metadata:
  type: project
  modified: 2026-10-16T19:35:52.549Z
---

Thread "A local judge that predicts online" (root cmsg_017gbamt2g1g8hMHRHQBc6qbX1fjpEFgMtKJSwjEKyCnKT), report in its branch. Site-map games won of 170 on the 12:52-based panel / the v51-based panel: v52 fixes3 133/124; fixes2 130/117; v50 anti_feed 124/115; v49 capture_fix 121/115; v51+draft 120/121; v51 fixes1 116/118. Online: v52 39%, v51 26%, v52 level with v50.
- fixes3 beats v51 on both panels (27-10 p=0.008; 20-14); fixes2 beats v51 only on the 12:52 panel (22-8 vs 16-17); the new-maps draft rule +4/+3 (under noise).
- **Noise floor:** v51 rebuilt four times with fuel-only changes scored 116-124, two copies disagreed on up to 20 games; identical source = identical bot, so any code change shifts fuel use by 4-8 games. Specialist opponents share code with the bot they were built from, so rules like protect allies behave differently against each set. Same 17 maps, deterministic engine: not maps or seeds.
- No single control: v49/v50 here are the teammate's folders at commit 3a2d263 on the fixes branch, not the uploaded zips. The judge's old label "v49 = im_p" corrected to v48. Gate recognises the active bot from its recorded zip.
**How to apply:** call a switch a win only if it clears ~10 flips vs v52 on both specialist sets (12:52-based and v51-based), site maps both sides; v52 is the confirmed base ([[cambc-teammate-fixes2]]). Related: [[cambc-local-judge]] [[cambc-online-versions-1016]] [[cambc-new-maps-strategy-1016]].
