---
name: cambc-online-versions-1016
description: 2026-10-16 timeline of what is online: ga65a6 = v44 (10:46), 12:52 +mono+fuelguard+jackpot (noise vs ga65a6), 15:20 im_p zip = v49 (slightly better than study27-economy, 43-34 pairs), 18:01 teammate fixes zip = v51 (bot B vs v49); 18:18 judge predicts v51 <= v49; 18:5x v52=fixes3 online 30% vs v49 39%, worse (flips 21-10)
metadata:
  type: project
  modified: 2026-10-16T19:10:00.000Z
---

**10:46-12:52 UTC:** mybot_ga65a6.zip (study27-economy + GA fight params, I030, no P_MONO) = site v44; 12:52 online = ga65a6 + P_MONO + P_FUELGUARD + P_JACKPOT (mybot_ga65a6_mono_fuelguard_jackpot.zip), recorded with --zip in versions.jsonl.

**12:52 close-out (15:11, 300 games):** 97-203 (32%); vs ga65a6 28-31 on 92 pairs = noise; vs study27-economy 56-48 on 168; stampede 2-18, contest 4-13, monolith 5-7; ranked 31-34. We die early while farming, not contesting the centre ([[cambc-new-maps-1016]], [[cambc-stampede-jackgo]]).

**15:09-15:20 UTC:** user uploaded mybot_online1252_jackgo_imitation.zip (im_a retreat) at 15:09; after im_a was found to die 89 vs 34 against the caster bots, user chose "Swap to im_p" and uploaded mybot_online1252_jackgo_imp.zip at 15:20 = 12:52 bot + stampede centre rule (P_JACKGO 350, P_JACKN 3) + im_p (fight like Mite only with an ally within 2 tiles). im_a had no clean batch; 15:46 is the first clean im_p batch. See [[cambc-stampede-jackgo]] [[cambc-replay-imitation]].

**15:46-17:5x batches labelled 'v49' in hourly.md** were in fact v49 (15:5x) and v50 (16:5x, 17:5x); see the 19:08 correction below.

**18:01 UTC user uploaded mybot_teammate_fixes1.zip** (site v51) (teammate bot + CAMPFOE, BACKHOME, NEEDHEAL, KITEALLY, NOCHASE2, TWIN; [[cambc-teammate-fixes]]) and asked to run the loop on it: bot B of the A/B, headline pairs vs v49, plus vs study27-economy. v49 ran 15:46-17:5x (3 batches).

Rule: versions.jsonl rows carry upload time + zip; online_base picks the newest by time (PR #29). Related: [[cambc-online-is-economy]] [[cambc-online-loop]] [[cambc-stampede-jackgo]] [[cambc-replay-imitation]].

**18:18 local judge:** predicted v51 no better than the then-online bot (panel 28-20 against v51, dies 14/game vs 9). 

**18:5x batch (125 games), user says it played as v52 = fixes3 (mybot_teammate_fixes3_mapdraft.zip), site verification pending: 38-87 (30%)** vs 39% for v49 over 3 batches. By rival rank: top 10 7-48 (13%; v49 19%), 11-20 27-33 (45%; v49 51%), 21-30 1-4 (v49 24-16). Per map: collision 11-14, corners 12-13, elkring 2-23, interlock 5-16, lanes 7-18, stampede 1-3; elkring and interlock sink (v49 23-59, 26-48). Paired vs v49 33-44 of 113; flips 21 for v49, 10 for v51 (68% > 57% tie threshold). Vs study27-economy tie 25-27 on 89 pairs. Local judge prediction confirmed. If confirmed, the online verdict goes against fixes3's local 136 vs 113 (elkring, interlock drop).
**10-17 site labels:** v54 09:08 simkitew; v55 10:53 teammate varg; v56 12:10 simw_all; v57 12:13-12:30 teammate cambc-v55-camp-state-fix (5 games); v58 13:16 teammate mate_bwf_upload (active ~13:20). Loop batches by label: v53 35% (12 batches), v54 29%, v55 27%, v56 31% (vs v53 43-46 noise), v58 21% (vs v53 24-37, flips 13-26, clear loss); v59 14:41 teammate battlecode_mate_all_wards_alerts_v2 17% (vs v53 24-46, flips 9-31), worst of the day. Teammates upload without telling the loop: check /submissions every tick.
