---
name: cambc-micro-tracking
description: 2026-10-16 per-champion fight memory P_TRACK on v52 (track.h): what v52 sees, vision facts, 5 uses measured on the site-map panel, none above noise; best = retreat toward remembered allies +4/170; retreat variant +40% fuel loss, rejected 19:58; 20:20 fuel fix P_ROSTER+P_OCMEMO: lost turns 106->12, identical games, merged into combined zip
metadata:
  type: project
  modified: 2026-10-16T19:46:48.564Z
---

Thread "memoria por campeón" (branch claude/micro-tracking-dt9bxp, no PR). Report + track.h + patch on v52:
/mnt/project-files/analysis/micro-tracking-2026-10-16/README.md (also in the repo under analysis/).
- Facts: vision is per champion, ~8 tiles (~200 tiles); a champion sees its live allies only 35% of turns; enemy
  is_alive() works out of vision; at our deaths 1.9 visible foes within 8 vs 0.2 unseen-but-remembered ("ghosts").
- P_TRACK 0 = byte-identical games to v52. Tracker alone costs ~3-5k fuel/turn and -3/170.
- Site maps (170 games, v52 121): Lanchester engage (FAV 100/140) 119/120, isolated weak enemy (ISO 3/5) 117/118,
  retreat toward remembered allies (P_TRACK_RET 6) 125 (+4, p=0.65; vs tracker-only 10-3 p=0.09). All within ±5-9 noise.
- 20:10 user asked to ship RET if cheap: lean version (allies only, fight turns only) = 120/170 (the +4 was noise) and
  fuel-exhausted turns 106 -> 149 on 34 site games (lanes 19->36, corners 8->24): not merged, not handed to the fixes thread.
  Details: /mnt/project-files/analysis/micro-tracking-2026-10-16/README.md section 4.
- Zip mybot_v52_trackret.zip (v52 + P_TRACK 1 + RET 6) for an online test only if the user wants; not uploaded.
- Sharing ally positions beyond vision would need repacking the 8 shared bytes (all used); not done (no gain to justify it).
**How to apply:** don't re-try ghost counts / power-based engage on the panel; the lesson is missing out-of-vision info is rarely near our deaths. Related: [[cambc-teammate-fixes2]] [[cambc-game-mechanics]] [[cambc-local-judge]].

**20:20 v52 fuel fix (decisions unchanged):** P_ROSTER 1 (champion roster read once; bc::champions(team) costs 3-23k per call) + P_OCMEMO 1 (other_captures memoised per round/group/tile; averaged 48k in fuel-exhausted turns). Unlimited fuel: 34/34 site-map games identical to v52. Fuel-exhausted turns, 17 site maps x 2 sides vs sp_castera: 106 -> 12 (monolith 51->0, lanes 19->8, stampede 14->0, corners 8->2); panel 118/170 vs 121 (noise). Patch /mnt/project-files/analysis/micro-tracking-2026-10-16/fuelfix_on_v52.patch, zip /mnt/project-files/bot/mybot_v52_fuelfix.zip, branch claude/micro-tracking-dt9bxp; handed to the fixes thread for the combined zip. Optional on top: P_TRACK 1 + P_TRACK_RET 6 (retreat toward remembered allies, zero API calls) = 20 lost turns, 123/170; fuelfix_ret_on_v52.patch / mybot_v52_fuelfix_ret.zip; coordinator recommended leaving it out (noise), user decision pending.
