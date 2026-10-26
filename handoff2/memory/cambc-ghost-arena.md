---
name: cambc-ghost-arena
description: "Ghost" test opponents built from ladder replays (a bot that walks a top-10 team's recorded route and fights what it meets); how to build one, how faithful it is, results so far
metadata:
  type: project
  modified: 2026-10-13T16:25:00.000Z
---

The hunter bot is a weak proxy for the top 10, so on 2026-10-13 (15:30-16:30 UTC) we built
**ghosts**: `arena/tools/ghost/mkghost.py DUMP.jsonl 1 bots/gh_NAME` turns a replay dump
(`replaydump.js REPLAY.zip --camps`) into a C++ bot (`ghost_template.cpp`) that drafts the same
champions and follows the recorded team's path as waypoints, with the recorded events attached:
camps hit (it lingers until the camp dies), tributes, recalls, purchases. It attacks any enemy
champion within 4 (lowest health first, spells included), recalls below 30% health once nothing
is hitting it, buys strength shards on spawn. Build with `cambc build bots/gh_NAME`; play it as
side b with `arena.py bots/X bots/gh_NAME --maps maps_pool/MAP.map26a --sides a` so our bot is on
the recorded side. Six ghosts exist (dumps in `arena/ghost_dumps/`): cabbage_corners,
cabbage_collision, cabbage_lanes, tip_corners, antifreeze_collision, hinana_corners (all v3td
ladder losses). `ghrun2.sh PREFIX BOT` runs the six games, `lanes.sh PREFIX BOT...` runs several
bots in parallel, `ghsum.py out/PREFIX_BOT NAME...` prints deaths and gems inside the recorded
game's length next to the recorded game.

**Fidelity:** inside the recorded windows v3td dies 34 times over the six games where the real
teams killed us 93 times, and the ghosts die 60 times where the real teams died 11. The ghosts
walk the real routes (they do hold the centre on corners/collision/lanes) but fight and farm
worse than the real teams, so they measure "do we walk into their pack" rather than "can we win
the fight". Games are deterministic, one game per ghost: differences under ~15 deaths over the
six games are noise.

**Results (deaths in window, v3td 34):** v8c 43, all-fight-rules 42, intents 37, actions 39,
heal/fortress 29, value focus 37, twin 45, eco 45, spell4 31, blocking 51, strength shop 33, bail
34; contested-camp lockout (`patch_feed.py`, P_CONTEST) farms slower and dies as often, the altar
guard (P_ALTAR_GUARD) sends champions on 40-tile tribute trips (3-15 vs v3td). Nothing beats v3td.
Pack play (`patch_pack.py`: two trios, leader claim adopted by followers, one capturer): see
[[cambc-bot-project]] for the outcome.

**Why:** the ladder is the only test against the real top 10; ghosts are the closest offline
proxy and cheap (6 games, 3 min). **How to apply:** test any anti-feeding or pack idea against
the ghosts AND vs v3td (farming) before offering it; to add a ghost, dump a ladder replay and run
mkghost.py. To make ghosts sharper, improve their fight logic in `ghost_template.cpp` (kiting,
focus with allies) and re-run every variant, since results only compare within one ghost version.
