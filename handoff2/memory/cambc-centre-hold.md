---
name: cambc-centre-hold
description: 2026-10-14: fight maps are won at the centre altar; kill loot; P_HOLD (v20) won locally but went 0-7 online on corners/collision, rejected
metadata:
  type: project
  modified: 2026-10-14T08:04:58.716Z
---

08:00 UTC 2026-10-14, while testing the caster draft ([[cambc-micro-strategy]]):

- **Killing a gem carrier gives its gems to the killers** (kill loot; replays show the victim's bag
  reappearing in the killers' carried gems, no event). Top fight-map winners loot 130-230 gems a game
  and the losers capture 300-400 fewer gems than the winners because they spend rounds dead.
- **Top teams bank at the centre altar** on corners (35,34, 4 gem-cluster pots of +48 next to it),
  collision (27,20, two wolves next to it) and interlock (19,16 / 20,23). Univardisty on corners: whole
  team at the centre from r20, wiped Mite there at r60-80 and sat on it. 56-80% of loser deaths are
  within 10 tiles of the map centre.
- Our caster draft (m2) farms camps 15-25% slower than the melee draft and fights only 1-9k champion
  damage a game (top caster teams 22-48k on corners), so casters alone did not help (m2 2-8 vs v19).
- v19's P_DANGER 3 makes us leave the centre when 3 enemies group there: the opposite of the top teams.

**P_HOLD N** (fbase main.cpp, default 0): the hold point is a reachable altar with |d(my spawn) -
d(enemy spawn)| <= 4 and 2+ gem camp groups within P_HOLD_R 6. Only corners (35,34) and collision
(27,20) qualify. Those camps score xN/100 and ignore danger spots; the altar ignores the danger and
own-half penalties. First test vs v19 (k5) on the 5 fight maps: kh1 (k5 + HOLD 300) 7-3, kh2 (200)
7-3, mh1 (caster draft + HOLD) 4-6; all three won collision and corners 4-0 (corners in ~340 rounds).
Ladder ghosts (tools/ghall.sh) are too weak to separate bots (k5, kh1, mh1 all 11-0). Pure farming vs idle is
15% slower with the hold (corners 276 -> 316 rounds), but vs any opponent it wins. Caster draft + hold (mh1)
still lost elkring, interlock and packs 0-6, so the caster draft stays off.

**08:06 UTC: study12 = site version 20** (`bot/mybot_study12.zip`, main/params/fight_study12, arena bot
`study12`) = v19 + P_HOLD 200. Identical to v19 except on corners and collision. Arena: 4-0 vs v19 on those
two maps, 4-0 vs hunter2 (v19 3-1). **Online v20 (ws/ours12, 08:10 batch vs the top 10): 7-28, corners+collision 0-7.** Holding the centre
fed the top caster teams: deaths 21 (VeryGood collision), 17 (Univardisty collision), 13 (VeryGood corners),
15 (Quantom corners) vs 4-12 for v16/v17 on the same pairings; their Stellar/Tavi/Cassi cast at range 4.4-4.8
for 270-380 a spell. P_HOLD rejected; advised reactivating v19. Lesson: local opponents (v19, ghosts,
hunter2) do not fight like the top caster teams, so fight rules that win locally keep failing online.

**How to apply:** build variants with `ws/tools/mkfrom.sh NAME BASE "#define ..."`; profile round use with
`ws/tools/timeuse.py`, gem sources with `gemsrc.py`, bank/death places with `topaltar.py DIR MAPS`.
