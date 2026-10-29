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
