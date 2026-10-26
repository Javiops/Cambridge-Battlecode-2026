---
name: cambc-sparring-v27
description: 2026-10-14 "Mejor sparring": caster sparring built on v27's engine (spar11/12/16) that beats v27 like real caster teams; fix results; v29
metadata:
  type: project
  modified: 2026-10-16T09:50:53.075Z
---

13:26 UTC 2026-10-14 the user chose "Mejor sparring" (build local rivals that kill like the online ones, then
retest the death fixes). Follows [[cambc-top1-study]].

**Online v27 by rival draft (caster maps, ws/ours27):** vs caster drafts (2+ of Stellar/Tavi/Willow/Prism:
VeryGood, glyph team, 剑桥夜爬者, hello, OneTap) 0-12, 10.7 deaths, Stellar 2.6; vs melee drafts (Varg/Ryth/
Vendetta/Ren/Marcella: Shawn, Still_Testing, Nyxius...) 14-12, 7.8 deaths. Old spar7-10 lost to v27 26-22.

**New sparring (fbase, `maps_cast` = collision/corners/elkring/interlock/packs, 10 games each):** spar11 =
study19 + P_DRAFTCAST 1 (VeryGood draft with v27's engine): v27 4-6, 10.2 deaths; spar12 = + P_BALL 5: 5-5;
spar16 = spar11 + P_SQUISHY 300 (sparring-only switch: prefer ranged targets): v27 3-7. Panel spar11+16+12:
v27 12-18, deaths 267. Melee sparring spar14/15 (P_DRAFTDIVE 1, Shawn's draft) too weak (v27 8-2): our melee AI
does not dive like Shawn. Our Stellar still dies less locally (1.3) than online (2.6).

**Fixes vs the panel (30 games):** u6 = P_UNI_FLEE 35 **20-10, deaths 226, kills 224**; u13 (+P_UNI_STAND 1,
_HP 0) 19-11; u10 (stand guard only) 19-11; u7 (FLEE 45 = v28) 16-14, deaths 291; u8 14-16; Ren kite u11 10-20.
u6 also: gen vs v27 44-44, hunter2 18-0, vs v26 14-4. **13:35 UTC: study21 = site version 29** (= u6;
bot/mybot_study21.zip, main/params/fight_study21), uploaded; v28 (study20) is worse on the panel.
Tools: tools/champdeaths.py (arena per-champion deaths), scratchpad dmgshare.py / bydraft.py.
**16:38 UTC: the user reports v29 is active and the team climbed to #25 on the ladder.**
2026-10-16 09:50: study27-economy beats spar11/12/16 both sides 67-8 / 85-4 / 65-9 on 100 fresh maps; the panel no longer discriminates near the current bot (see [[cambc-ga-micro]]).
