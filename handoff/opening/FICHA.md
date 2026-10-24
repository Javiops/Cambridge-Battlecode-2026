# Opening pieces on v157 (= bundles/monoguard-v1c.zip 87e46a7d)

## ope = opening-near-v1e (zip 3592f071)
Near maps (spawn-to-spawn path < 35), rounds <= 30, Vendetta/Heart of Ruin/Marcella only: gem-bearing groups farther than
6 tiles of walking are priced down, score x (6/travel)^1 (P_OP*, params.h). Why: online top 10 near maps hit the first camp
at r6 (Vendetta) / r11 (HoR) vs our r24 / r22, same damage per hit (farmexec.py), nobody buys before r40.
Local near test (120 g vs 6 rivals): team monster damage net r20 +342 / r40 +475 (v157 -40 / +50), but r300 gold +146
(v157 +188), a14 logit@300 +0.48 vs +0.59. Hard panel vs v6d -21/480 (far +1 mid -12 near -10); v157 alone -5.
Sent as an ONLINE MEASUREMENT (stall thread): online rivals contest middle camps, local rivals do not. Judge: monster damage
net r40/r100 and state at r300 on near maps.

## hpb = hitpass-v2 (zip 93e274df)
End of turn, attack unused: hit a camp in reach that is awake and within 2 of our hits of dying, or a 1-hit cluster of a
guardless group; never monolith/golem. Fires ~1.4 times/champion by r400. Local a14 +0.54 vs +0.59 (neutral), hard panel -7/480.
