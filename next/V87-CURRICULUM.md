# V87 field curriculum, 21 October 2026

**V87 / ppo-topdraft-v12 remains compiled and active.** All 44 requested unranked groups / 220 games are collected and independently verified through the official 1.0.1 engine. Every queued and completed own version is 87. All 35 maps are covered in both seats. Final actual allowance: zero. Automatic ranked and incoming games are excluded. Final team observation: #143 / 1,674 Elo; peak #9 is historical.

The result is **75/220 wins, zero faults and one fuel-exhausted turn** (ambush B versus Tozo). Historical comparison strata: 44/120 nearby, 31/80 stretch, 0/20 leader. Current opponent ratings overlap these labels, so they preserve historical strata rather than prove a current strength order. With the preceding 30-game, three-version banking benchmark, this collection session uses 50 challenge groups / 250 games at 150 nearby, 80 stretch and 20 leader games. Do not pool mixed bot versions to claim strength.

The same 220 map/opponent/seat labels in historical v83 data have **87 wins and 70 fuel losses**, versus v87 75 wins and one. This is a descriptive repeat, not a controlled causal estimate: opponent submission equivalence for old B-seat games and engine seed equivalence are not independently certified. Aggregate results have regressed; the runtime and banking fixes alone have not made this a stronger bot. Retain it as a working experiment under Fran's iteration policy, with v86/v85/v83 preserved for rollback. No lab promotion or independent PPO gain is claimed.

## Map diagnostics

Means are per game and include the small leader sample where present. Collection is lifetime acquisition, not final inventory; the difference from deposits also includes loss, theft and timing. Boss-battle may resolve on gold with zero banks. Map/opponent/draft remain confounded.

| Map | Wins | Banked | Collected | Gold | Deaths | Fuel losses |
|---|---:|---:|---:|---:|---:|---:|
| 00ambush | 1/6 | 708.2 | 728.3 | 3477 | 7.7 | 1 |
| 00collision | 3/8 | 454.5 | 515.6 | 4084 | 21.6 | 0 |
| 00contest | 0/6 | 33.3 | 266.7 | 4120 | 76.2 | 0 |
| 00corners | 3/4 | 1000.2 | 1035.5 | 7045 | 10.2 | 0 |
| 00eight | 2/4 | 757.5 | 869.5 | 5862 | 30.2 | 0 |
| 00elkring | 0/4 | 412.2 | 531.2 | 2655 | 30.0 | 0 |
| 00expanse | 0/2 | 897.0 | 897.0 | 6010 | 0.5 | 0 |
| 00fragment | 3/6 | 574.3 | 627.8 | 6485 | 20.0 | 0 |
| 00interlock | 3/6 | 777.7 | 860.8 | 5367 | 19.7 | 0 |
| 00lanes | 5/6 | 801.8 | 824.5 | 7947 | 10.8 | 0 |
| 00monolith | 4/12 | 849.9 | 967.8 | 7174 | 18.9 | 0 |
| 00packs | 3/6 | 689.8 | 710.2 | 4787 | 13.7 | 0 |
| 00pilgrimage | 2/6 | 490.7 | 555.7 | 5207 | 43.0 | 0 |
| 00quadrants | 0/6 | 571.3 | 634.0 | 1725 | 15.3 | 0 |
| 00reverse-spiral | 0/6 | 321.3 | 620.5 | 1783 | 67.3 | 0 |
| 00rows | 9/10 | 965.1 | 1029.8 | 8882 | 9.0 | 0 |
| 00rushbait-v2 | 4/6 | 969.2 | 1172.2 | 6872 | 11.2 | 0 |
| 00split | 0/6 | 399.0 | 524.2 | 1155 | 31.5 | 0 |
| 00stampede | 4/8 | 449.0 | 550.0 | 4905 | 39.1 | 0 |
| 00swirl | 1/6 | 303.2 | 344.8 | 4608 | 61.8 | 0 |
| 01big-world | 0/4 | 402.8 | 428.2 | 3118 | 11.8 | 0 |
| 01boss-battle | 2/6 | 0.0 | 110.2 | 2767 | 26.5 | 0 |
| 01broken-curve | 1/6 | 605.7 | 644.3 | 3332 | 12.0 | 0 |
| 01concentrated-wealth | 3/6 | 817.0 | 897.8 | 6632 | 11.5 | 0 |
| 01corridors | 5/6 | 874.2 | 918.2 | 7893 | 11.7 | 0 |
| 01elk-arena | 1/8 | 406.2 | 471.0 | 8668 | 49.9 | 0 |
| 01fracture | 0/8 | 399.8 | 461.8 | 5619 | 19.5 | 0 |
| 01gold-rush | 2/8 | 571.1 | 618.8 | 2452 | 35.1 | 0 |
| 01hooks | 1/6 | 298.8 | 394.2 | 2590 | 68.5 | 0 |
| 01islands | 2/6 | 37.3 | 37.3 | 237 | 1.3 | 0 |
| 01shortcut | 1/6 | 513.7 | 880.8 | 2373 | 24.8 | 0 |
| 01starfish | 1/6 | 299.2 | 547.7 | 5013 | 76.7 | 0 |
| 01starvation | 3/6 | 382.0 | 487.3 | 2773 | 46.0 | 0 |
| 01the-farm | 4/8 | 631.2 | 744.9 | 4255 | 12.0 | 0 |
| 01yellow-brick-road | 2/6 | 781.3 | 950.7 | 8953 | 62.7 | 0 |

## Next hypotheses

- Big-world banks most acquired gems in the new sample but still loses the race. Improve productive acquisition and control rather than assuming the old stationary banking failure persists. Preserve the independently reproduced v8 banking gain.
- Contest has both acquisition failure (Tozo: 0 collected/0 banked, 73/90 deaths) and delivery failure (Cozy A: 1,200 collected/0 banked, 56 deaths). Trace carrier decisions and nearby threats before selecting one general change. Do not add map-name cases.
- Elk-arena can collect/deposit successfully in one seat while collapsing in another. BitShift B wins with 972 collected/900 banked; A collects zero and dies 50 times. Antifreeze yields 76/88 deaths. Inspect sustained objective damage, reward control and disengagement separately.
- Pilgrimage remains exposure-sensitive: Dirty Coding loses with 44/60 deaths, while both Context Overflow seats win despite 43/48. Death count alone is not the policy target.

Freeze one coherent tested fix per next version, screen both seats on official and generated development layouts including large geometries, reproduce the release binary, then automatically upload usable experiments with short notes. The 70 reserved confirmation maps remain unplayed; all historical Stage 1–7 certificates, trained weights and consumed holdouts remain intact.

Source ZIP SHA256: `63307a7f21d3dc877914fd4f3bbedd24c92ad8777e7275c8e98b3cd93bf6a8de`. Independently rebuilt local release WASM: `fcd2cdc3c2c69e8defc939f28d1145e60aa8fb176466dc4ef720ccdbf8bd96ea`. The server-downloaded source matches; server compilation/live status are verified without claiming a server binary hash.

Reproduction: set CAMBC_NODE to the bundled Node executable, then run `python work/analyze-banking-field.py v87-curriculum-20261021-r1` in the restored workspace. Native reconstruction matches terminal winner, round, banks and per-champion gold, deposits, collection, kills and deaths for all 220 games. The package includes official maps, raw replay bundles, summaries, source, native audit outputs and hash manifest.
