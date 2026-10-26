---
name: cambc-v53-review-1017
description: 10-17 review of v53 online games: user directive that the fight verdict must model real damage (both sides, cooldowns, emblem passives, focus items); wards best switch so far
metadata:
  type: project
  modified: 2026-10-17T09:04:44.652Z
---

On 2026-10-17 (morning) the user reviewed v53 online games (Nameless, Silver Samurai, Eternal Wisdom) and listed fight cases in the thread "Revisión de partidas de v53" (thread id cmsg_017gbamt2g1g8hMHRHQBc6qbDuHeM3HDGpCbdyxCp1DSxJ, branch claude/v53-replay-review-qop5ws, switches on bots/v53, all off by default).

Findings so far (switches measured as game flips vs v53 on the 12:52 panel / v51 panel):
- Wards on (P_R5_WARD): +10 / +6, deaths down vs casters and hunters. Best of the day, just under the +10/+10 bar.
- No spells on camps with a rival at <= 6 tiles: +4 / +2.
- No dash while farming at start or after seeing rivals: +7 / 0.
- Real spell damage + emblems in the power ratio with the old 0.6 cut: -1 / -11 (makes us leave winnable fights; cut must be recalibrated, ~0.45 tried next).
- Re-judge every round, deposit-safe, ask-for-help: noise.

USER DIRECTIVE (08:32): the real-damage model can only help; keep working on it. The fight verdict must count real damage for rivals and for us: spell multipliers per champion, cooldowns, emblem passives, and how many items give focus. Judging a fight correctly depends on these.

**Why:** v52/v53 power = hp x damage with fragments only; items (300 gold gaps), emblems, real spell multipliers and readiness are ignored, so the bot takes 2v2s it loses.

**How to apply:** any new fight-verdict work builds the full item/spell/cooldown model and recalibrates the cut, rather than dropping the idea because the first measurement lost. See [[cambc-v53]], [[cambc-fight-verdict]], [[cambc-panel-noise]].

**09:04 round results (flips vs v53, panel 12:52 / panel v51):** wards alone +10/+6 (best, ~2 fewer deaths per game vs casters and hunter) = /mnt/project-files/bot/mybot_v53_ward.zip (v53 + wards, nothing else; upload is the user's call, asked 09:04). Full two-sided fight model (cooldowns, stuns, emblems, Ren passive, Cassi+Issac shared hp) +4/+2 at cut 0.6, +4/-2 at cut 0.4; its AUC for predicting a lost fight is 0.632 vs 0.587 for the old formula (16,344 fights, never-flee bot), so the model judges better but acting on "leave" by fleeing just moves the death (2 of 3 deaths happen fleeing). User idea 08:52: kite + call for help instead of fleeing (P_PVKITE: name nearest foe in shared memory, hold tile and shoot while no foe can reach next round, step back toward allies only when one can): +3/-1 old formula, +7/-2 full model = tie. Full model + wards +10/-2, + kite +7/-2: combinations do not stack.
