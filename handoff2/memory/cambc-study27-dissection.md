---
name: cambc-study27-dissection
description: 2026-10-15 13:21 online dissection of study27 vs study26 (155 games each vs top 30): stacking works on 3000+hp maps at no cost, keep 27; rows end-game and tribute-cancel are the next gains
metadata:
  type: project
  modified: 2026-10-15T13:22:47.608Z
---

Report: /mnt/project-files/analysis/v35-dissection-2026-10-15/study27-vs-26.md (+ positions_27, fights_27, reactions_deaths_27, farming_27 beside it, every table 27 vs 26 side by side). Verdict from the Dissect thread: **keep study27**.
- Stacking (P_MAX_SHARE 4 / P_STACK_HP 3000) fires only on 3000+hp groups (rows, expanse, elkring). Rows: 3.26 attackers per pack vs 2.66, 4-on-camp in 142/295 captures vs 18, big-camp kill 20 rounds vs 25, 17.4 captures/game vs 15.8, 961 gems tributed vs 891, reach 1000 at round 403 vs 421, half the idle streaks next to a living pack.
- No cost: deaths 5.8 vs 5.7/game, monster deaths 22 vs 25, small camps same speed, same idle/tributes. Fights, reactions, territory, deaths-at-home all within noise. 58-97 vs 59-91 overall is pairing noise (collision 12-7 -> 8-11 with identical fights/economy).
- Rows still 3-14: a race to 1000; we tie at round 300 (685 vs 688) but lose 300-400, one bag short in 11 of 14 losses with 99-165 gems in hand. Last 100 rounds the four-stack dissolves (shop recalls + respawns desync), last bags detour via shop (2 shop recalls in final 30 rounds), 33-gem split shares carried 60 rounds. Proposed rows end-game rule: no shop recall once anyone is within 150 of 1000, bank shares at once, keep the four on the wolf nearest the altar.
- Still deciding other maps: tributes never cancelled with an enemy walking in (23 deaths, 1436 gems; 4 of 5 biggest single losses are tributes at collision's centre altar); lanes leaves 1 champion vs 3-4 invaders; monolith's 2700-hp wolf pairs sit under the 3000 threshold (they stack 21%, we 4%); collision's 108-gem elk cluster never farmed.
- Expected-gain order: cancel channels on approach > rows end-game rule > stack threshold 2700 > fight rules from [[cambc-v35-dissection]].
Related: [[cambc-study26-fixes]] [[cambc-online-loop]] [[cambc-eval-method]]
