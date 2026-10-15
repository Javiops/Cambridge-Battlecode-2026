# study26: the 2026-10-15 fix list

study26 = study25 + three fixes that held up. Every item on the list is a switch in `params.h`, so each one can be
turned on or off and measured alone.

How it was measured: each switch alone against study25, from both sides, on 313 maps (official 9, maps_gen 44,
hold60 60, dev200 200). A map counts only when one bot wins it from both sides. Numbers are "maps won both sides /
lost both sides" (the rest split 1-1). A tiny change already moves about ±6 maps, so only a big gap means anything.

| # | item | switch | alone vs study25 (won/lost both) | in study26 |
|---|---|---|---|---|
| 3 | the dash check named Cassi; it is Issac (melee) that dashes. Cassi is ranged, so that name was never checked and an enemy Issac's reach was 2 instead of 3 | `P_DASHFIX 1` | 32 / 28 | yes (bug fix) |
| 2 | the attack reset only checked "target still alive" on corners and interlock | `P_U34_RESET_LIVE 2` (every map) | 25 / 16 | yes |
| 4 | area spells (Stellar 1.4 x focus, radius 1) aimed at one foe | `P_AOE 1`: aim at the tile covering the target and the most other foes; `P_AOE 2`: also cast it before the single-target spell when 2+ foes are under it | AOE 1: 14 / 7, AOE 2: 19 / 12 | `P_AOE 2` |
| 1 | check if a spell is worth losing the turn: maybe escape first | `P_CASTSAFE N`: before moving, skip a spell that roots us when we are below the flee threshold or the enemy's ready damage on our tile is N% of our health (a killing cast still goes) | N 70: 12 / 29; hp check only: 15 / 30 (dev200 6 / 20) | no, clearly worse |
| 5 | wards | `P_R5_WARD 1` | 55 / 58 (official 4 / 0) | no, noise |
| 6 | P_KITE runs before P_FRONT, so a kiting caster never uses the front-line rules | `P_KITEFRONT 1`: front line first, kite when it declines; `2`: kite shoots the team focus | 1: 17 / 13; 2: 5 / 5 | no, noise |

Together: dash + reset + AOE 2 (= study26) **50 / 40** (official 2/0, gen 8/4, hold60 10/8, dev200 30/28), p = 0.34.
Adding KITEFRONT 1: 48 / 40. Dash + reset + KITEFRONT 1: 43 / 40.
Caster sparring (spar11/12/16, official maps, both sides): study26 48-6, study25 47-7.

What we learned: escaping instead of casting lost every time. A ready caster that stands and shoots does more good than
one step away, which agrees with the top teams standing still in about half of their contact rounds.
