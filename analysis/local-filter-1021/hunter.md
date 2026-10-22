# Hunter rival (10-22 18:40 UTC)

Patch `panel/hunt.patch` (main.cpp only): before the first-contact verdict, any enemy champion within 10 with no other
foe within 5 of it is hunted (engage, never pv-leave / back off) if a mate is within 9 of it, or alone when our hp >= 0.6
and health >= 1.3x its health.

- **pHuntF** = pF (strongest panel rival: P_HALF 30, draft ryth/vesper/vendetta/varg/prism) + patch. Our bots win 66-80%.
- pHunt = pInv (invader, heart/stellar/ren/ryth/varg) + patch: too weak (we win 88-93%), few flips; gold@r400 still moves like online.

80 games per bot (40 site maps x 2 sides), cambc 3.0.4, paired like the panel.

| change (online verdict) | pHuntF net (bar) | deaths/g base->cand | gold@r400 | 9-rival panel | online gold@r400 |
|---|---|---|---|---|---|
| stallfix vs mate-dash (+11) | **+6** (7.5) | 8.8 -> 7.4 | | +16 | +1.0% |
| value vs stallfix (-9) | **-6** (8.0) | 7.4 -> 8.7 | -5.8% | +30 | -8.7% |
| goldw40-v2 vs stallfix (-7) | **-8** (7.5) | 7.4 -> 8.6 | -5.4% | +36 | -7.2% |
| elksplit-v1 vs stallfix (+1/-3) | -4 (7.5) | 7.4 -> 8.7 | -4.3% | +21 | -3.1% |
| need2 vs stallfix (+14) | -2 (8.0) WRONG | 7.4 -> 9.1 | +0.4% | +29 | +3.6% |
| marc-bfill vs need2 (+24) | +2 (8.9) | 9.1 -> 7.4 | +10.4% | +44 | +5.5% |
| mega-far vs marc-bfill (-7) | -2 (8.0) | 7.4 -> 7.4 | +1.0% | +18 | +4.5% |
| t10draft-v2 vs marc-bfill (+8/+14) | **+11** (9.6) | 7.4 -> 6.5 | +13.8% | +32 | +10.8% |

Signs right 7/8 (only need2 wrong) vs 4/8 on the 9-rival panel: every farm-macro change the panel liked
(value, goldw40, elksplit, mega-far) is negative on pHuntF, and their deaths rise +1.3/g as online (+1.5-2), panel +0.1-0.6.
pHunt (weak) signs: value -1, goldw40 0, elksplit 0, mega-far +1 (too few flips), gold value -11.1%, goldw40 -7.5%, need2 +2.9%.

Recommendation: add pHuntF to the panel as a veto rival (farm/macro change must be >= 0 on pHuntF and not raise its deaths);
80 games = 2 minutes on 4 cores.
