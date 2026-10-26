---
name: cambc-v35-dissection
description: 2026-10-15 deep dissection of our own 150 online v35 (study26) games vs top 30: farming equal, we lose by dying; measured reaction/fight-opening/retreat stats
metadata:
  type: project
  modified: 2026-10-15T12:22:00.000Z
---

Report: /mnt/project-files/analysis/v35-dissection-2026-10-15/README.md + positions, fights, reactions_deaths, farming
reports (per map, win/loss, top-10 vs 11-30, examples by match id and round), scripts_*/, data/steps.tgz (150 decoded
games, format DATA.md); also repo branch claude/project-thread-ztmd0i analysis/v35-dissection. 150 games (the 11:33 UTC
unranked batch, 59-91), 12:22 UTC, same metrics for us and the rival in the same game, Mite as second reference.

**Farming is not the problem:** alive, captures/100 champion-rounds 1.19 vs 1.21, gems per capture 35 both, bag 44 both,
we walk straighter (0.89 vs 0.84), idle 8% vs 10%. Expanse without deaths is a tie. (Minor farm gaps: first-camp
stacking, recalls after 50% of captures / 48% shop trips even where walking is shorter, recall retry 32% vs Mite 59%.)
**We lose by dying:** 858 deaths vs 581 (5.7 vs 3.9 per game), 13.6% of time dead vs 9%, 73% in our own half, from ~90%
hp in ~5 rounds, to spells (rival Stellar = 30% of kills). Causes measured: enemy visible a median 13 rounds before
first hit and we keep farming (23%), stand (16%) or approach (49%), move away only 10%; we open fights as often as Mite
(52%) but outnumbered 42% (them 26%) and with allies >8 tiles away 85%; our openings 0.69 kills / 0.58 deaths, theirs
on us 0.97 / 0.32; only openings on a rival that is farming, tributing or recalling pay; ranged hit from distance 1-2
35% (them 24%), only 8% of spells from 5+; we retreat at 50% hp one tile per round with the attacker adjacent, alone,
and die after retreating 19% (them 11%; casters 30% vs 13%); we never cancel a tribute or recall under fire (17 deaths
inside a tribute channel). Allies within 6 never attacked in 325/709 deaths. No territory answer: rival crosses into
our half 11.9x/game (us 2.9), captures in our half in 42% of games; mid-camp balance predicts wins 0%..87%. Squad
1.16-2.57 attackers by hp bucket vs Mite 2.0-3.5.
**How to apply:** fight changes should target: react when an enemy appears (group up or leave before the first hit),
open only with numbers/on busy targets, keep ranged at 4-5, cancel channels under fire. Ranked causes: not reacting to
visible packs > opening outnumbered > casters at 1-2 > no territory answer > farm. Related: [[cambc-top2-dissection]]
[[cambc-online-loop]] [[cambc-study26-fixes]].

**13:30 UTC study27 batch (155 games, 58-97) dissected the same way, report study27-vs-26.md in the same folder:**
stacking fires on rows/expanse/elkring only (rows 3.26 attackers vs 2.66, four-stacks 142/295, hit-to-capture 20 vs
25, +70 gems tributed, 1000 at r403 vs r421), no cost (deaths 5.8 vs 5.7, small camps unchanged); every fight/
reaction/position number identical within noise; 58-97 vs 59-91 is pairing noise. Verdict given: keep study27.
Rows still 3-14: level at r300, lose r300-400 by one bag (shop recalls in the last 30 rounds, 33-gem split shares carried
60 rounds, four-stack dissolves after r200); opponents bank at r392. Next: cancel channels on approach, rows end-game
rule, stacking threshold 2700 (monolith/packs pairs), farm collision's elk cluster.
