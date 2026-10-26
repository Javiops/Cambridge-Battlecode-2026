---
name: cambc-top10-study-1014
description: 2026-10-14 study of 169 distinct top-10 vs top-10 games: fight maps vs farm maps, caster drafts, invasions, shop; report and data paths
metadata:
  type: project
  modified: 2026-10-14T07:33:28.409Z
---

07:00 UTC 2026-10-14 the user said to stop bot work and "understand properly how the best teams are
playing" from 100 top-10 games. Report: `/mnt/project-files/analysis/top10-2026-10-14/how-the-top-10-play.md`
(data `top10_teams.jsonl`, `tables_by_map.txt`; tools `arena/tools/study/topstudy.py, topagg.py, topfights.py,
topinvade.py`; raw in ws/top10x, distinct set ws/top10u, ours in ws/oursx9 (v16), oursx10 (v17)).

Method facts: the engine is deterministic, so repeated challenges replay identical games; 235 downloaded
games (06:40-07:11) held only 169 distinct ones. Dedupe by (map, team a, team b, score) before stats.
Compact event kinds: k2 ak0 capture reward, k11 recall start, k12 submit start, k18 submit done, k13 buy.

Findings: fight maps (corners, interlock, elkring, packs, collision): the winner had more kills in 90 of 108
games, top losers die 12.5/game, 65% on their own half; winners invade from r52-62 (corners, interlock).
Caster drafts (Cassi&Issac + Tavi + Stellar, Univardisty/VeryGood, the two best at 63-64%) beat melee
drafts on corners 10-1, elkring 6-2, interlock 5-2, packs 5-2, lose on rows 2-5, expanse 0-3, monolith 0-2.
Top teams change draft by map; we draft the same everywhere. Farm maps (rows, expanse, monolith, lanes):
almost no fights; rows winners 63 gems/capture, 8% split, 81-gem bags (us 39, 64% split, 39). Us overall:
1.9 kills/game (lowest), 2% time in enemy half, 81% of deaths at home. Our Tavi buys strength; top Tavi
buys focus. Related: [[cambc-focus-farming]], [[cambc-public-match-data]].
