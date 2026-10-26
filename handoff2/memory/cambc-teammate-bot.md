---
name: cambc-teammate-bot
description: 2026-10-14 the user's teammate sent a bot = v29 + P_VOLLEY 70 + P_KITE_ZONE 4; tested vs v30/v29/v27/panel; v30 + the same two switches = study23 (best on the panel)
metadata:
  type: project
  modified: 2026-10-15T08:55:27.272Z
---

20:57 UTC 2026-10-14 the user's teammate sent fight.h/main.cpp/params.h. main.cpp and fight.h are byte-identical to
study21 (v29); params.h = params_study21 + `P_VOLLEY 70` + `P_KITE_ZONE 4` (no P_FINISH). Follows [[cambc-corners-long]].

Results (cambc 2.1.6, scratchpad ws, both sides; panel = spar11/12/16 on maps_cast, 30 games):
- teammate bot: vs v30 official 10-8 (+88 gems), gen 43-45; vs v29 13-5, gen 44-44; vs v27 12-6, gen 48-40;
  panel 18-12, deaths 197 (v29 18-12/238, v30 20-10/237 in the same run).
- study23 = v30 + both switches: vs v30 official 9-9 (+88), gen 43-45; vs v29 10-8, gen 50-38; panel **24-6, deaths 159**.
- v30 + P_VOLLEY 70 only: panel 21-9; v30 + P_KITE_ZONE 4 only: panel 19-11. Both together is best.
- Teammate switches cut deaths on official fight maps vs v30 (53 vs v29's 95).
Zip: /mnt/project-files/bot/mybot_study23.zip, params_study23.h; result logs in analysis/teammate/.
Caveat: P_VOLLEY 50 (v25) went 16-59 online after looking good locally ([[cambc-volley]]).

2026-10-15 07:40 UTC second version (de_rules.h, opening_replace.h, utility.h added) = teammate bot + known-map
fingerprint (v34de::classify by exact size/altars/walls: per-map tweaks on rows/lanes/monolith/expanse/packs/corners/
interlock; per-map drafts all off) + general changes (P_E_RETARGET 6, P_NE_POWER_OPEN melee power emblem first,
P_R5_LOCK altar lock, packed claims). fight.h = v29 (no P_FINISH). Zip as-is: bot/mybot_study24.zip.
Results: vs v30 official 13-5 (farm maps 7-1), **gen 54-34**; vs study23 14-4, gen 48-40; vs v29 15-3, gen 54-34;
panel **25-5, deaths 131** (best so far). Gen gain comes from the general changes (known-map rules do not fire there).
2026-10-15 wards: v30 has no ward code; study24 has the teammate's ward routine in utility.h behind P_R5_WARD (off by default). Switched on: 29-1 vs caster sparring (25-5 off), but loses 8-10 official / 41-47 generated head-to-head vs study24 without wards, and v30 gen 54-34 same as off. Kept off.
2026-10-15 08:53 UTC the user said site version 34 is live (code names its rules v34de, so likely study24 as-is; unconfirmed). Audit: analysis/audit-2026-10-15.md (score head-to-heads by maps won on both sides; the side-A farming gap was tested 09:50 UTC and is noise, see [[cambc-eval-method]]).
