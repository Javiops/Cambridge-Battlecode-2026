---
name: cambc-bot-project
description: CAMBC battlecode (cambc2026a) C++ bot at /mnt/project-files/bot/; versions (v3td = shipped zip, lean = fuel-fix candidate, v8c/flee40 reverted), ladder results, what failed and why
metadata:
  type: project
  modified: 2026-10-13T18:05:00.000Z
---

The user's CAMBC (Cambridge battlecode, event cambc2026a) bot is a single C++ file, shipped as
`/mnt/project-files/bot/mybot.zip` (`cambc bundle`: the zip holds `src/main.cpp` and `src/params.h`). Files in /mnt/project-files/bot/:
- `main_v1.cpp`: first version, lost 0-5 online. `mybot_v3.zip`: v3 (camp-group state, cooldown
  broadcasts, squad sizing, tributes).
- **Shipped 12:43 UTC 2026-10-13 ("v3td", = mybot.zip and mybot_v3td.zip)**: v3 + `params_tuned.h`
  + draft Vendetta, Varg, Cassi & Issac, Ryth, Tavi (the user's chosen order). Beats v3
  15-3 on the 9 official maps. Source: `bot/mybot/src/{main.cpp,params.h}`, `bot/main_v3td.cpp`.
  **Ladder with it: 12-38 (24%) vs the top 10** — see `analysis/ladder_v3td.md`: 0 wins on
  corners/collision/lanes with 8-12 deaths per game (walking one by one into the enemy team at
  the centre), a freeze next to a guarded altar on collision (champion standing on a dead camp's
  spawn tile blocks its respawn), rows/expanse lost on speed.
- **Rejected online**: v8c (pack caution, 4-51) and flee40 (earlier fleeing, 4-71): real teams run
  fleeing champions down. Afternoon fight-rule/economy/pack experiments on v3td: nothing helped.
  Details: [[cambc-fight-engine]], [[cambc-ghost-arena]], files `bot/mybot_v8c.zip`, `mybot_flee40.zip`.
- `mybot_lean.zip` = v3td + fuel fix ([[cambc-fuel-budget]]); `mybot_study.zip` = lean + 8 top-team
  habits ([[cambc-top5-study]]).

**Ladder lesson (13:36 UTC):** top teams hunt with trios all over the map taking almost no damage;
the arena "hunter" bot is a weak proxy (it cannot farm or focus-fire). Data:
`analysis/data/ladder_*/`, replays `analysis/replays/ladder_*/`. Playbook from their replays:
`analysis/playbook-top10.md`. Ghost opponents from ladder replays exist ([[cambc-ghost-arena]]); they say no local rule on v3td
reduces deaths, so the gap is pack play + fight quality + economy together.

**Why:** build on the arena-tested version; do not repeat the v4-v8 or afternoon detours.
**How to apply:** before shipping run `arena.py BOT bots/v3td --maps 'maps_pool/*.map26a' --sides
both` ([[cambc-arena-setup]]), check deaths vs `bots/hunter2` and the ghosts, `cambc bundle`. Games
are deterministic: only +-30 deaths or several wins in 18 games are real. See [[cambc-user-prefs]],
[[cambc-game-mechanics]], [[cambc-public-match-data]].

**18:00-18:50 UTC (study thread 2):** `mybot_study2.zip` (= study minus P_SHOP_PLAN, 17-1 vs v3td)
was uploaded and played online: wins vs top-10 teams, most series lost 2-3, but collision scores
of 44-322 because collision's altar 39,20 is walled in and champions chose it when 27,20 was
locked/occupied, then stood still for 100-350 rounds. `mybot_study3.zip` (18:50, main_study3.cpp +
params_study3.h, built by `arena/tools/study/patch_fight2.py` on main_study2) adds P_ALTAR_REACH,
P_UNJAM, P_UNSTICK 30 and fight rules P_ENGAGE2 120 + P_LOWHP 50 (arena: 17-1 vs v3td, 11 deaths
vs 37; 9-9 head-to-head vs study2). `mybot_study2fix.zip` = study2 + only the freeze fixes.
Rejected in arena: P_UNSTICK 8, P_WALKHOME, P_ENGAGE2 150, P_CARRY 22, P_NODASHIN, P_ALLYDUTY.

Later versions (study4, study5, the online test loop): [[cambc-study-versions]].
