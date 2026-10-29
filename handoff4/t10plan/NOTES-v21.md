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
