# t10plan-v21 (2026-10-29, cloud): v17 + HoR self-shield whenever ready in combat

v18 9/80, v19 9/80 (kvvl 9, v17 10): neither passes. v20 (v17 without the v14/v16 leave rules) 81/140 local: not sent.

## 1. Fights (online v17 c37, `an/odds.py`, champion-killed deaths r30-300, allies/foes within 6 five rounds before)
| per game | us (v17) | rival |
|---|---|---|
| outnumbered (foes > allies+1) | 1.30 | 0.35 |
| even | 0.72 | 0.34 |
| ahead | 0.25 | 0.33 |
| total | 2.27 | 1.01 |
Stats are close (r300: max hp 1249 vs 1360, strength 60 vs 64, items 2.3 vs 2.9): the even fights are lost on execution.

## 2. Heart of Ruin (engine end-of-game statistics, ext.py meta, 75 online v16 games)
| per HoR game | us | rival |
|---|---|---|
| shieldingDone | 5,188 | 16,895 |
| abilities per 100 alive turns | 6.4 | 14.3 |
| kills / deaths | 0.68 / 4.0 | 2.67 / 0.81 |
Rival Varg (self-shield too) 20,731. No other champion we draft shields. Cause: support_spells cast the shield only under 85% hp.

## 3. v21
`P_V21 1`: the shield is cast whenever ready in combat (foe within 4 or awake camp near). Local 16 games, side a: HoR shield
18,149/game (v17 9,402). Local 84/140 vs kvvl (v17 92). Zip `zips/e1foco-t10plan-v21.zip`, diff `src/t10plan-v21_vs_v17.diff`.

## 4. v21 online: 12/80 (kvvl 9: 7 for, 4 against, +3, bar 6.6; v17 +2). Best so far; new base.

## 5. v22 = v21 + HoR dash in the damage estimate (`an/abil.py`, `an/abilctx.py` on ext.py decodes of v17 c37)
Whole game: rivals earn 6,919 gold vs 3,537 and collect 1,130 gems vs 556; monster damage per champion ~2x.
Away from fights (no foe within 4, r30-600) the rival HoR does 25.7 basic attacks per 100 alive turns, ours 11.8 (others 15-21
vs 17-27). Per-hit damage is equal (HoR basic 32-33, dash on camps 132-136). r30-300 camp attacks per HoR game: rival 59 basic +
17 dash, ours 22 + 11. `my_dps` read HoR as strength 30 (her damage spell is the dash, not in the estimate), so squad admission
kept her out of groups. v22 adds 29% of the dash damage (the rivals' dash/basic ratio). Local: HoR camp attacks r30-300 35 basic +
13 dash per game (v21 27 + 11), 94/140 vs kvvl (v21 84, v17 92). Zip `zips/e1foco-t10plan-v22.zip`, diff `src/t10plan-v22_vs_v21.diff`.

## 6. v22 online 11/80 (kvvl +2, v21 -1): v21 stays the base.

## 7. v23 = v21 + reset shot after a kite step (fight::kite)
`an/abilctx.py` (v17 online, r30-600, foe within 4): our Vesper does 32 basic attacks per 100 fight turns, rival Vespers 49; the other
champions are within 3-7. A ranged champion that steps cannot attack; kite steps first and then tries to shoot, which fails. The
attack reset (Vesper) gives the attack back after a step, but it was only used after a hit (double shot). v23: after a kite step,
with the focus in range and the reset ready, cast it and shoot. Local 82/140 vs kvvl (v21 84); fires in 121/140 games.
Zip `zips/e1foco-t10plan-v23.zip`, diff `src/t10plan-v23_vs_v21.diff`.

## 8. v23 online 8/80 (v21 -4): closed. v24 = v21 + P_PV_ER 6 -> 8
Outnumbered deaths are the largest class (v17 online r30-300: 1.30/game vs rival 0.35; 42% with no ally within 6). The fight
verdict and the v14 every-turn judgement count and weigh foes within P_PV_ER; at 6 the killer is already at 1-2 tiles when the
leave fires. 8 = the whole view: judged earlier, ratio with every foe in view. Local 85/140 vs kvvl (v21 84).

## 9. v24 online 9/80 (v21 -3): closed. v21 online, first 11 games: HoR shield 9.6k/game (v17 5.0k, rival 16.9k).
## v25 = v21 + wider shield trigger
support_spells also runs its shield with a foe within 6 or after a camp hit last round (v21: foe within 4 or an awake camp near).
Local 16 games side a: HoR shield 25.3k/game (v21 18.1k). 93/140 vs kvvl (v21 84). Zip `zips/e1foco-t10plan-v25.zip`.

## 10. v25 online 9/80 (v21 -3, 2/5 all close maps). Since v17 every candidate is 8-12/80 against kvvl 9 with a bar of ~6.5:
c37 cannot tell single rules of this size apart. v26 = v21 + v22 (HoR dash in my_dps) + v19 (P_NEED_CAP 3), the changes whose
mechanism moved as designed and that did not lose online by more than 1 game. Local 82/140. v21 full online replays (`an/abil.py`,
`an/ahead.py`): HoR monster damage 7.5k vs rival 19.3k, HoR deaths 3.44 vs 0.72; our champion-killed deaths with more allies than
foes within 6: 2.99/game vs rival 0.90.

## 11. v26 online 9/80 (v21 -3). v27 = v21 with Varg in HoR's draft slot on near/mid maps (Ren stays on far maps)
Aimed at the big gaps, not a 2-4 game rule. Online v21 (80 games, engine end statistics): our HoR 7.5k monster damage and 3.44
deaths a game, rival HoR 19.3k / 0.72; rival Varg (9 games) 38.5k / 0.33, the best farmer seen (splash basic attacks, attack
reset, self-shield; varg.h and the shield/splash code paths already exist). Local 16 games side a: slot-1 monster damage Varg 28.4k
vs HoR 12.5k, team gold 6.94k vs 6.51k a game; 87/140 vs kvvl (v21 84). v27b (Ren on every map) 87/140, Ren 18.7k: not sent.

## 12. v27 online 8/80 (v21 -4, close maps 1 vs 5): HoR + shield beats Varg. v21 stays the candidate.
Online scoreboard since v17 (kvvl 9/80): v17 10, v18 9, v19 9, v21 12, v22 11, v23 8, v24 9, v25 9, v26 9, v27 8.
None passes the bar (~6.5). Measured gaps that remain (v21 online, whole game): gold 3.5k vs 6.9k, deaths 13.6 vs 2.8,
champion-killed deaths with more allies than foes near 3.0 vs 0.9 a game; the allies near a dying champion deal damage in the
same share as the rival's (37% dealt nothing in 10 rounds, both sides), so no single rule behind it was found.

## 13. Structural tries on v21 (late game grouping; deaths after r300 are 1.4-3.0 per 150 rounds vs rival 0.3-0.8)
| bot | change | local vs kvvl |
|---|---|---|
| v28 | from r300 every non-carry escorts the nearest carry, every map | 59/140 |
| v28b | from r300 the HoR/Ryth roles on every map (not only near) | 72/140 |
v21 = 84. Both lose a lot locally (grouping costs farm, as the block line v9-v12 showed); not sent. Diffs in src/.

## 14. v29 = v21 + leave when invaded alone on our own half
Online v21: 54% of our champion-killed deaths are on our own half (rival 32%), 42% with no ally within 6 (rival 30%).
verdict.h v14_judge: alone (no ally within 6) on our own half with 2+ foes within 8 (one within 6) -> leave (walk home / recall),
whatever the power ratio. No grouping. Local 89/140 vs kvvl (v21 84). Zip `zips/e1foco-t10plan-v29.zip`.

## 15. v21 re-judged: 160 fresh games 21 vs kvvl 13 (+8); 240 games +11 (bar 11.1). v29 online 9/80 (v21 -3).
## v30 = v21 without the v14/v16 leave rules (P_V14 0, P_V16 0)
Every leave rule added online lost to its base (v24 -3, v29 -3; v16's dash leave raised dash deaths 0.24 -> 0.31) while fighting
stronger (v21 shield) gained. Fled deaths are caught anyway (killer at 1-2 tiles). Local 86/140 vs kvvl (v21 84).

## 16. v30 online 6/80 (v21 -6): the v14/v16 leave rules help; adding more leaving hurts (v24, v29), removing it hurts more.
## v31 = v21 + durability-h emblem for Marcella and Vendetta
End-of-game items, v21 online: durability emblems held per champion-game (10% less incoming damage): rival Marcella 0.74, Vendetta
0.67, Vesper 0.76, HoR 0.50; ours Marcella 0, Vendetta 0 (Vesper 0.82, HoR 0.35). Same direction as the v21 shield: be harder to
kill. Plans: Marcella treasure-f, bruiser-f, jungle-s, +durab-h, bruiser-h x2...; Vendetta treasure-s, jungle-s, +durab-h, bruiser-h...
Local 96/140 vs kvvl (v21 84).
