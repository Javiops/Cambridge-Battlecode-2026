# fight120 (2026-10-27): even contacts vs the top 5 (engine 2.0.0), candidate o120c on e1foco

Measured on t5b e1foco replays (claude/pc-e1-assets, 103 decoded), contacts r21-200 that start even (allies = foes within 4):
fight4.py (targets, abilities, exits) and fight4b.py (per ability slot).
| | us | top 5 |
|---|---|---|
| kills / deaths per contact | 0.10 / 0.21 | 0.24 / 0.06 |
| ability in the first 2 rounds | 54% | 71% (Vesper 65 vs 97, HoR 50 vs 74, Vendetta 64 vs 86) |
| hit the lowest-health foe (2+ in reach) | 55% | 67% |
| champion under 50% that leaves alive | 59% | 83% (our Vendetta, with the o95 cut, 81%) |
| Vesper reset per 10 contact rounds, distance | 0.93, 2.5 | 1.20, 3.0 |
| HoR shield: health at use, in first 2 rounds | 0.54, 17% | 0.67, 29% |

Local filter, 420 games (p17_rTop1/rD/mV19, 70 maps, both sides), e1foco = 304; probe +20 changed 0 games.
| variant | wins | + / - | bar |
|---|---|---|---|
| o120 (Vesper shot after kite step + HoR early shield) | 291 | +33 / -46 | 17.8 |
| shot after step only | 303 | +32 / -33 | 16.1 (fires almost never) |
| early shield only | 290 | +22 / -36 | 15.2 -> off |
| o120b: Vesper steps into reach, resets, shoots (+ shot after step) | 300 | +37 / -41 | 17.7 (reset uses +5%) |
| **o120c = o120b + o95 cut for HoR, Ryth, Vesper** | **308** | +55 / -51 | 20.6 |
o120c local deaths per game: Vesper 2.23 -> 1.79 (gems 226 -> 246), HoR 1.85 -> 1.74, others equal.
zips/e1foco_o120c.zip, stdout marker "[init] o120c". Flags: P_VSTEPSHOT, P_VSTEPIN (P_VSTEPIN_HP 50), P_CUT_ALL; P_HSHIELD_EARLY 0.
