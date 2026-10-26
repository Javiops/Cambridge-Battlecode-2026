---
name: cambc-user-own-bot
description: 2026-10-14 10:18 the user is building their OWN bot from scratch with a farm draft and a fight draft; advise on optimal play, not our bot's limits
metadata:
  type: user
---

2026-10-14 10:18 UTC the user said: "don't think with our current restrictions, the fact that our bot does not
want to stay still doesn't mean we should play unoptimal drafts; I am building my own bot from 0".

**Why:** they want to learn to code and to design the strategy themselves; our bot's limits (moves every round,
so casters never cast) are not theirs.
**How to apply:** when they ask strategy questions, answer with what is optimal in the game (top-10 data, engine
facts such as damage spells of Tavi/Ryth/Cassi needing a still round), and treat our bot's weaknesses only as
lessons. They have two drafts: farm and fight, chosen from map measurements in the draft
([[cambc-unseen-maps]]). Coach, don't write their code unless asked ([[cambc-exercises]]).

10:37 UTC: their from-scratch starter is docs/ejercicios/mi-bot/main.cpp (+ mi-bot.zip): own attempt/norm, path<45 -> FIGHT_DRAFT
else FARM_DRAFT, idle game. Trap found: looping bc::to_string over 48 champion ids every draft round runs out of
fuel from round 3 (engine then picks random champions); build the champion list once in the first draft turn.

10:38 UTC feedback: after I handed them a finished starter bot, the user said "your job is to guide me through the
implementation". **How to apply:** one step at a time: say what the next piece must do, which bc:: calls/signatures
to use, and the pitfalls; let them write it and review what they paste. No full solutions unless they ask.

11:15 UTC: user set up a clean local workspace C:\Users\Javier\Cambc2026 (cambc 2.1.6 via `py -m pip`; Python314\Scripts
added to user PATH) and `cambc new --lang cpp mibot`. That starter has main.cpp (loop: play_draft()/bot.play_turn() in
try/catch, then end_turn), draft.cpp (play_draft once per draft round, random pick of ids 0-10, draft_memory =
string_view), bot.cpp (move_towards_closest with distance_field). Guide them on that structure (step 1 = their
FARM/FIGHT draft in play_draft, static to measure once), not on our bot's run_draft. Nothing was deleted in the project.

11:36 UTC feedback: after I gave a wrong instruction (delete starter files, not needed), the user said "please, this
competition is important". **How to apply:** build/run every instruction in the scratch workspace (ws/bots/mibot
mirrors their setup) before sending it; say what was verified. Fact: with no pick, run_draft printed only once on rows.

12:10 UTC: for their fight/draft design, cite analysis/top1-2026-10-14/como-juega-el-numero-1.md (#1 team: 28-1 on fight
maps, 12-16 on farm maps; 3-4 damage casters buying focus, cast standing still from 4 tiles, open fights, leave <30% hp).
12:00 progress: mibot draft.cpp prints team/size/dist (corners 40, rows 73); next = pick from FIGHT/FARM list by dist.

Draft map-type work (zones, POI distances, greedy route) continues in [[cambc-user-draft-route]].
