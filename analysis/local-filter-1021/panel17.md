# V17 panel (22-oct, 22:15 UTC)

The old 9-rival p panel is saturated: t10shop-v2 wins 87% of its games. The new panel has 10 rivals on the
**t10shop-v2 brain** (V17), with the top-10 shop plans for the champions that have one:

- rA, rB, rC, rD, rF, rE, rG, rM: the old pA..pM drafts. rD is close to our own draft (heart, ryth, vesper, vendetta, marcella).
- rInv: rM draft, P_HALF 250, no doorstep penalty (invader).
- rHunt: rF draft + hunt.patch (hunts lone champions, see hunter.md).

Sources are in panel17/ (also bundles/panel-v17.zip). Compacted base results are in base-results-v17/ for t10shop-v2,
t10draft-v2 and marc-bfill-v1. Runner: `bash scripts/runpanel17.sh WORKDIR CAND NAME [JOBS]`, with BASE=t10shop-v2 by
default. 800 games take about 20 minutes on 4 cores; stats are compacted afterwards and replays deleted.

## Base win rate (games won out of 80 per rival)
| bot | total | rA | rB | rC | rD | rF | rE | rG | rM | rInv | rHunt |
|---|---|---|---|---|---|---|---|---|---|---|---|
| marc-bfill-v1 (V15) | 51% | 44 | 35 | 37 | 21 | 25 | 49 | 50 | 46 | 66 | 34 |
| t10draft-v2 (V16) | 65% | 55 | 51 | 44 | 39 | 34 | 62 | 62 | 59 | 67 | 44 |
| t10shop-v2 (V17) | 74% | 66 | 61 | 57 | 47 | 34 | 64 | 69 | 68 | 74 | 53 |

Online, V17 wins about 57%. rD, rF and rHunt are the hard rivals; rInv is soft.

## Calibration (paired net out of 800; online scale = x120/800)
| change | V17 panel | per 120 | online |
|---|---|---|---|
| t10draft-v2 vs marc-bfill | +110 (214/104, bar 35.7), deaths 10.7 -> 8.4 | +16.5 | +14 in 2 batches (+7/120) |
| t10shop-v2 vs t10draft-v2 | +76 (157/81, bar 30.9), deaths 8.4 -> 6.2, gold@400 +3.7% | +11.4 | +4 b1 (batch 2: see the API thread) |
| mega-far vs marc-bfill | **+46** (107/61, bar 25.9), gold +3.3% | +6.9 | **-7** (wrong sign) |
| mega vs marc-bfill | **+41** (150/109, bar 32.2), gold +3.2% | +6.2 | **-3** (wrong sign) |
| marc-bfill vs need2 | +73 (192/119, bar 35.3), deaths 11.9 -> 10.7 | +11 | +24 in 1 batch (right sign) |
| fixpack-v1 vs t10shop-v2 | -2 (107/109, bar 29.4), gold -1.0% | -0.3 | -1 |
| shootfirst-v1 vs t10shop-v2 | +35 (116/81, bar 28.1), gold +3.4% | +5.3 | +1 |
| gemrace-v4 vs t10shop-v2 | +27 (71/44, bar 21.4), gold -1.2% | +4.0 | +5 then -3 |
| tribfirst-v1 vs t10shop-v2 | -6 (72/78) | -0.9 | not sent |
| tfhor-v1 vs t10shop-v2 | +10 (94/84, bar 26.7); far maps 0 | +1.5 | not sent |

**Farm macro is still overrated** (as on the p panel). Use panel17 for power, draft, shop and fight changes; for farm/macro
changes the veto is pHuntF (mega-far -2 there, right sign). rFarm1 (map thread, far farmer) results to follow.

Both power changes give the right sign, at about 2x the online size, as on the old panel. The panel moves about 2x as
many pairs (238 vs 106 for t10shop-v2), so it can see again.

## Reading the panel (23-oct, 04:40 UTC)
Scaled to one batch (x120/800), the three V17 candidates that came out flat online are -0.3, +5.3 and +4.0. All three
sit inside one batch's noise (about ±6), which is what online showed. **To expect a pass in one online batch (bar about
11-12), a candidate needs about +80/800 on panel17**, in practice 2x that because the panel inflates power changes about
2x. Farm macro: panel17 is not a judge (mega-far +46, mega +41 while online was negative); use pHuntF as the veto.
Mechanism rivals, 80 games each (fixpack / shootfirst / gemrace-v4 / mega-far vs marc-bfill): rFarm1 -4/-3/+4/+3,
pHuntF 0/+2/+3/-2, rRush1 -1/+6/+3/+2. All are within noise (bar 6-11).

## Extra mechanism rivals (sources in panel17/, base results in base-results-v17/ for t10shop-v2 and marc-bfill-v1)
- rFarm1 (map thread: far farmer), rRush1 (farm thread: first big camp at r90 with a trio), and **rRushHunt = rRush1 +
  hunt.patch**. Against rRushHunt t10shop-v2 wins 72% (online ~57%) and dies 8.7 times a game, the closest to the
  online band of any rival so far. Its verdicts are the right size, not the right sign: fixpack -1, shootfirst +2,
  gemrace-v4 +2 (online -1/+1/+2 summed), mega-far +1 (online -7).
- To run them, add them to the rival list (RIV in my chainV.sh; in runpanel17.sh, edit the two rival loops).

## Base V18 = nightpack-v2 (10-23 10:56), 960 partidas
- WR en panel17: 78% (V17 74%).
- panel17 (10 rivales) contra t10shop-v2: **+31/800** (98 a favor, 67 en contra; barra 25.7). Escalado a un lote online son +4.6/120.
- Por rival: rF +13, rHunt +7, rA +5, el resto entre -1 y +4. Oro@400 +1.0%.
- Muertes 6.31 -> 6.28 por partida, Vesper 1.90 -> 1.93. La excepción es rD: 6.6 -> 8.2 y Vesper 1.7 -> 2.4, con net +1.
- rFarm1 y rRush1: +3 en 160.
- Los resultados están en `base-results-v17/cal_nightpack-v2_*`.
- `runpanel17.sh` y `runmech.sh` usan ahora BASE=nightpack-v2 por defecto. Las bases V17 siguen disponibles con `BASE=t10shop-v2`.
