---
name: cambc-study-versions
description: CAMBC study4/study5 bot versions (2026-10-13 evening): what each adds, offline numbers, site version numbers, how candidates are measured
metadata:
  type: project
---

**19:30 UTC: study4 = v12** (`mybot_study4.zip`) = study3 + P_SHOOT 1 (a champion backing away still hits
the weakest foe in reach after its step; 110 of 177 study3 deaths came with no attack in the last 6 rounds).

**20:15 UTC: study5 = version 13 on the site** (`mybot_study5.zip`, main_study5.cpp + params_study5.h) =
study4 + P_SHOP_PLAN 1 (damage-first shop, all 3 top-10 reports agree) + P_PAIR 2 (2 bodies on gem
clusters). Pure farming vs an idle bot (`tools/farmbench.sh`, rounds to 1000 summed over 9 maps): study4
3958, shop 3752, study5 3786. Round robin vs s4/e1/lo1/study/lean/v3td: 68-40 (study4 ~56-52), interlock
8-4; but hunter deaths 27 vs 5. Rejected by farmbench: P_STEPOFF (slower), P_OWN_ALTAR 0, P_NOGOLD,
P_CHAIN 44/16, P_POT (corners centre hold; untestable offline). Reports: analysis/top10n/.

**Online study5 (v13, 60 games, ws/ours5):** 19-41; deaths 5.5/game, Cassi+Issac 51% of deaths.
Team renamed "Live Love Larp": fetch by team id 292625c5-0f3a-49f0-a08a-9757b8f58658.

**20:50 UTC: study6 = version 14 on the site** (`mybot_study6.zip`: main_study6.cpp + params_study6.h +
fight_study6.h; arena bot `g2`) = study5 + P_HITFIRST 1 (melee hit before stepping back; ranged step
first, measured that a ranged attack blocks moving) + P_SAFESTEP 1 (back off to the tile fewest foes reach,
toward an ally). Arena: 11-7 vs study5, 17-1 vs v3td, 16-2 vs lean, ghosts 6-0 d6, hunter d34, fuel same.
Rejected single rules: P_PACKOPEN 50 (farmbench 3982, slower), P_GANG 3, P_CALLHELP alone 7-11. Promising
next: P_TWIN (hunter deaths 25->11; with g2 = `h5`, 10-8 vs study5) and P_ALTAR_SAFE 30 (`h6`, 10-8).
Online games after v14: ws/ours6 (fetch_ours.py ours6 2026-10-13T20:50).

**Stopped 21:30 UTC 2026-10-13 (user: "enough for today; tomorrow I give more input and we work
together", so propose and wait for their input before big moves).** v14 online, 65 games (ws/ours6,
tools/vcmp.py ours5 ours6): 22-43 vs v13 19-41; deaths/game 4.9 vs 5.5, attacks on champions 49 vs 42,
deaths alone 78 vs 112; Cassi+Issac still 55% of deaths -> P_TWIN is the next candidate. Corners 0-11
across v13+v14: the rival takes the centre pots (34-36,31-37) with all bodies by round 17 and we
walk in one by one (VeryGood: 120 dmg done vs 20394 taken, 14 deaths). Ghost `gh_verygood_corners`
(from that replay) reproduces it: study6 scores 0 gems in 2000 rounds, 50 deaths. Untested fix in
fbase main.cpp: P_DANGER N (an enemy pack of N within 4 marks a danger spot for P_DANGER_T rounds;
skip camps within P_DANGER_R, altars nearby +60; shared via byte 7 when P_CALLHELP is off). Variants
d1-d3 not built yet. 21:33: user said to take P_TWIN as given: `mybot_study7.zip` = study6 + P_TWIN 1
(main/params/fight_study7), arena after: 13-5 vs study6 (209 g/100r), hunter d31, ghosts 6-0 d10,
beats gh_verygood_corners 1006-600 (study6 0-598, 50 deaths). Online (ws/ours7, 21:34) it was WORSE:
0-25 vs Mite/Kratos/BitShift/WHIM/SHINK (study6 6-19 vs the same teams), many close losses. Advised
reactivating v14. Closed 21:45: TWIN did run (Cassi-Issac within 2 with a foe
near: 45% vs 23%) but Cassi deaths stayed 1.4/game, banked gems at r300 -5%, deaths 5.3 vs 5.1. P_TWIN rejected
(tools/vcmp2.py, twincheck.py). Arena 13-5 + ghost wins did not predict online. Weak ghosts: gh_nova/kratos/whim_corners.

How to measure a candidate (study thread, 2026-10-13): build with `ws/tools/mkf2.sh NAME "DEFINES"` (fbase +
study4 switches), farming speed with `farmbench.sh TAG BOTS` (vs `bots/idle`), fights with `stbatch.sh`, head-to-head only vs the site version
(`rrvs.sh TAG BOT c1`, see [[cambc-user-prefs]]). Copies of the tools in
/mnt/project-files/arena/tools/study/. Online loop: [[cambc-site-access]]. Related: [[cambc-bot-project]].
