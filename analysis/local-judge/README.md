# Fixing the local judge (2026-10-16)

Problem (user, 14:49 UTC): since the GA genomes reached main, local wins have not shown up online. Online gives
~30 challenge groups an hour; locally we tune to beat our own bot instead of the top teams.

Three parts: (1) how well local verdicts predicted online, (2) a panel of specialist sparring opponents, one per
way we lose, validated against replay statistics, (3) how to spend the online quota.

## 1. Calibration: local verdict vs paired online result

Online side: `calib_online.py` (reads `/mnt/project-files/online/data/games.jsonl`, unranked games only). For each
version change it keeps the latest game of each (opponent, map, side) per version and counts the pairings that flip
(won with one version, lost with the other). Version windows are in the script (from `versions.jsonl` / `hourly.md`).

| change (new vs old) | kind | local verdict | local share | online shared pairings | online flips new-old | online share | p (sign) | P(online this low if local were right) |
|---|---|---|---|---|---|---|---|---|
| study27 vs study26 (stack on 3000+ hp camps) | farm | 154-106 maps won both sides, every set | 59% | 125 | 15-18 | 45% | 0.73 | 0.08 |
| study28 vs study27 (cancel doomed tributes) | fight | dev200 24-5 | 83% | 137 | 12-10 | 55% | 0.83 | **0.002** |
| corners fix vs study27 (fires on corners only) | fight | corners panel 16-0 (vs study27 itself 2-0) | - | 313 (corners 41) | 39-39 (corners 6-4) | 50% | 1.00 | - |
| ga65a6 vs overnight bot (GA fight weights, v44) | fight | sealed 560 maps 180-79 | 69% | 209 | 27-20 | 57% | 0.38 | 0.05 |
| 12:52 combined vs ga65a6 (P_MONO + fuel guard + jackpot) | bug/farm | fresh 71-56, site maps 23-11, contest and stampede won both sides | 56% | 79 | 7-4 | 64% | 0.55 | 0.79 |
| 12:52 combined vs overnight bot | | | | 127 | 19-16 | 54% | 0.74 | |

"Overnight bot" = 15 Oct 17:09 to 16 Oct 07:47: study27 + corners fix, then study27-economy from an unknown time
(the source matched Fran's branch at 08:05). Online numbers for the combined version are the 13:5x batch only.

Per map, the GA change (ga65a6) moved where the GA was trained on fights: corners 5-0, lanes 5-1, elkring 4-1,
rushbait 3-0 for; interlock 1-4, monolith 0-3 against. The combined version's target maps did not move online:
contest 1 flip in 14 pairings (still 0-7 raw), stampede 1-1.

### What the table says

- **No version change since 15 Oct was decided online** (every p >= 0.38), while local called four of them clear wins.
- **Local overstates the size of fight changes.** If study28's local 83% had been true, seeing 12-10 online has a 0.2%
  chance; for ga65a6 (69% locally) 27-20 has 5%. Local self-play magnifies fight changes because both sides run our
  code: a fight tweak that exploits our own fight rules wins big against us and barely registers against Mite or Univardisty.
- **Farm and bug fixes predict better.** Stacking and the fuel guard came out at local 56-59%, online 45-64%: consistent
  within the online noise. The farm side of the local judge is not the problem; the fight side is.
- **Half of the online flips are not the bot.** The same version, replayed on the same (opponent, map, side) an hour later,
  changes result 8% (study27) to 13% (overnight) of the time, because rivals upload new bots. Version changes flip
  14-26% of pairings, so roughly half of every online A/B is rival drift.

### How much an online hour can tell (feeds part 3)

Pairings that flip at all, over every (opponent, map, side) played by two or more versions:

| map | pairings | ever flipped | our win % |
|---|---|---|---|
| collision | 39 | 54% | 62% |
| interlock | 41 | 54% | 50% |
| packs | 42 | 52% | 36% |
| lanes | 43 | 44% | 31% |
| elkring | 40 | 42% | 34% |
| corners | 41 | 41% | 43% |
| rushbait_v2 | 16 | 31% | 40% |
| monolith | 40 | 30% | 41% |
| fragment | 16 | 25% | 26% |
| expanse | 46 | 24% | 43% |
| rows | 44 | 20% | 33% |
| ambush | 15 | 20% | 30% |
| swirl | 18 | 17% | 36% |
| stampede | 12 | 17% | 18% |
| pilgrimage | 14 | 7% | 11% |
| contest | 14 | 7% | 2% |
| eight | 15 | 0% | 0% |

| rival rank | pairings | ever flipped | our win % |
|---|---|---|---|
| top 10 | 139 | 28% | 19% |
| 11-30 | 228 | 41% | 38% |
| 31+ | 129 | 29% | 53% |

The six fight maps (collision, interlock, packs, lanes, elkring, corners) flip about twice as often as the rest;
eight, contest and pilgrimage almost never flip (we lose them whatever the version). Rivals ranked 11-30 flip most;
the top 10 mostly beat every version we have uploaded.

## 2. What online actually looks like: 153 of our games vs the top 30, decoded

`tools/panel/gamestats.py` on 153 replays of our bot (ga65a6 and the 12:52 build, 16 Oct 10:46-15:00, rivals ranked 1-30,
18 per map) and on the 101 Mite/Univardisty games of 15 Oct. Same definitions for every row: a contact turn = alive
with an enemy within 8; died10 = dead within 10 rounds of a contact turn; retreat share = steps that increase the distance
to the nearest enemy, among steps with an enemy within 5. Rows: `online_rows.jsonl`, `top2_rows.jsonl`.

| team | games | win% | deaths/game | deaths before r500 | kills/game | gems/100 rounds | gems carried at death | died10 | retreat share at hp 30-40 / 40-50 / 50-60 / 60-70 / 90-100 |
|---|---|---|---|---|---|---|---|---|---|
| us vs top 30 | 153 | 29 | **14.1** | 8.0 | 4.8 | 92 | **81** | **14.9%** | 0.45 0.42 0.30 0.24 0.20 |
| top 10 vs us | 63 | 84 | 2.9 | 1.9 | 14.4 | 143 | 22 | 2.8% | 0.38 0.33 0.25 0.21 0.17 |
| rivals 11-30 vs us | 90 | 62 | 6.1 | 3.4 | 13.9 | 117 | 72 | 5.6% | 0.39 0.35 0.28 0.25 0.17 |
| Mite (15 Oct, vs top 20) | 54 | 63 | 4.9 | 4.1 | 4.9 | 189 | 54 | 7.3% | 0.54 0.31 0.22 0.18 0.10 |
| Univardisty (15 Oct) | 54 | 48 | 6.1 | 4.5 | 6.4 | 156 | 106 | 8.2% | 0.44 0.36 0.31 0.28 0.15 |

What costs games online is one symptom far above the others: **we die, 14 times a game, carrying 81 gems each time,
and kill 5.** Retreat decisions are close to theirs (a few points more cautious); farming is not the gap where we live
(rows, lanes, monolith, expanse: 0-3 deaths, 215-250 gems/100 rounds). The deaths pile up on contest (62/game), stampede
(37), swirl (28), eight (19), fragment (17), pilgrimage (15).

### The specialist panel

The user's direction: one local opponent per way we lose. Each specialist is the online bot (12:52 zip) with switches
(`tools/panel/specialists.txt`, built by `tools/panel/build_panel.sh`); the hunter adds `hunt.h` (P_HUNT, sparring-only,
off = the online bot unchanged; `patch_hunt.py` inserts it). Every fight specialist uses the top teams' retreat cut at
~40% hp and no chase limit.

| specialist | symptom it covers | what it does |
|---|---|---|
| sp_castera | loses team fights | Univardisty caster draft on every map (5-champ variant too), moves as a ball, prefers squishy targets, gangs lone foes, calls fights at worse odds |
| sp_casterh | dies while farming + team fights | caster draft + 2 hunters that patrol our camps nearest our spawn and our altars, chase the foe with most gems |
| sp_hunt | dies carrying gems / intercepted at camps and altars | our draft + the 2 hunters |
| sp_centre | too defensive / objective fights | holds the centre altar with its camps (P_HOLD 400, radius 8), farms the enemy half (P_HALF 250), never leaves when grouped |
| sp_farm | farms too slowly | avoids every fight, pure race |
| (new maps) | loses on new maps | a map set, not an opponent: the 17 site maps + generated cousins + sealed fresh sets, as today |

Our online bot against each, 17 site maps both sides (34 games), next to online (153 games vs the top 30):

| opponent | our win% | our deaths/game | our kills/game | per-map correlation with online: deaths / win% |
|---|---|---|---|---|
| **online, vs the top 30** | **29%** | **14.1** | **4.8** | |
| sp_castera | 53% | 11.3 | 6.2 | +0.97 / **+0.50** |
| sp_caster (calls fewer fights) | 56% | 11.4 | 6.6 | +0.96 / +0.50 |
| sp_casterh | 71% | 12.8 | 11.3 | +0.96 / **+0.53** |
| sp_centre | 82% | 10.3 | 15.0 | +0.41 / +0.41 |
| sp_hunt | 82% | 12.9 | 11.7 | +0.97 / +0.06 |
| spar16 (old caster sparring) | 91% | 4.6 | 9.1 | +0.48 / +0.22 |
| sp_farm | 88% | 4.7 | 6.6 | +0.90 / -0.50 |
| our own bot (self-play) | 59% | 8.2 | 8.1 | +0.91 / +0.29 |

- The caster specialists are the closest thing to the top teams we can build: they kill us almost as often as online
  (11-13 deaths a game vs 14) and their map-by-map results follow online's (win% correlation +0.5, self-play +0.3, the
  old caster panel +0.2).
- **No specialist is as lethal as the real top teams.** They trade kills with us (6-15 kills for us a game) where the top
  10 lose 2.9 champions a game. Every specialist is built from our own fight code, and our fight execution is what
  loses online; the gap is execution (spell damage, focus), not decisions: our retreat curve is already within a few
  points of theirs.
- sp_farm is not informative (negative correlation, we beat it everywhere but on race maps); keep it only as a farm-speed
  check.

### Does the panel rank versions the way online did?

`tools/panel/panel.py` played the three last online versions against sp_castera, sp_casterh, sp_hunt, sp_centre and
sp_farm on the 17 site maps + hold60 (77 maps, both sides, 2,310 games; `panel_versions.json`).

| pair | self-play local | panel: games that flip | online: pairings that flip |
|---|---|---|---|
| ga65a6 vs study27-economy | 180-79 maps (69%) | 114-67 (63%), p=0.001 | 27-20 (57%), p=0.38 |
| 12:52 build vs ga65a6 | 71-56 fresh (56%) | 79-50 (61%), p=0.01 | 7-4 (64%), p=0.55 |
| 12:52 build vs study27-economy | | 126-50 (72%) | 19-16 (54%), p=0.74 |

The panel's direction agrees with online on all three and its size is closer than self-play for ga65a6 (63% vs 57%
online, self-play said 69%), but it still overstates, most for the 12:52 build. Expected: the specialists are built
from the 12:52 build's own code, so that build has a home advantage against them (sp_farm alone gives it 28-12).
**Use the panel to rank candidates that share the online bot's code, never to compare against an older code base.**

### Pre-registered prediction: im_a (online since 15:09)

im_a (imitation thread: P_UNI_FLEE 33, P_LOWHP 40, P_GA_AVOID_HP 45, P_AVOID_DIST 2) went online at 15:09 inside
mybot_online1252_jackgo_imitation.zip. Written down at 15:50 UTC, before its online batches:
- self-play gate: im_a better, 63-38 maps (p=0.017)
- the imitation thread's caster check (spar11+16, 36 games): our deaths 89 vs 34, wins 32 vs 34
- **specialist panel: im_a worse, games that flip 46-68 (40%, p=0.049)**; it dies more against every fight specialist
  (castera 6.4 vs 5.4 deaths, centre 9.9 vs 7.5)
The online paired result for im_a vs the 12:52 build settles which judge to trust (the jackgo stampede rule rides along,
so compare on non-stampede maps).

## 3. How to spend the online quota

What the calibration says about online information:
- A version change flips 14-26% of the shared (opponent, map, side) pairings, and 8-13% flip anyway between hours
  with the same version (rivals upload new bots). With today's mix of maps and rivals an hour yields ~100 shared
  pairings and ~20 flips, half of them drift.
- To call a real 60/40 split of flips at p<0.05 with 80% power needs ~190 flips; 65/35 needs ~85. At ~20 flips an
  hour that is 9-10 hours per comparison, which is why no change since 15 Oct was decided.

Recommendation (for the Dissect thread, which owns the loop):
1. **Fixed design, every game a pairing.** Challenge the same 30 rivals every hour with explicit `mapIds`, so every
   game of hour B repeats a game of hour A. Today only 50-80% of games pair up.
2. **Flippable games only.** Use the six fight maps (collision, interlock, packs, lanes, elkring, corners: 41-54% of
   pairings ever flip) and rivals ranked 11-30 (41%), plus a few top-10. Drop eight, contest and pilgrimage (0-7% flip)
   and the race maps rows, expanse, swirl (17-24%) from A/B hours: a fix there is checked deterministically on the
   local copy of the site map, and one online group on those maps only confirms the uploaded build behaves as locally.
   This roughly doubles flips per hour (~45-60), so a 65/35 effect shows in ~2 hours per version, 60/40 in ~4.
3. **ABAB, then stop.** Alternate hour by hour A, B, A, B. The two A hours measure rival drift on the same pairings;
   subtract it before judging. Decide at p<0.05 on flips; if after 2 hours each the flip share is under 57%, call it a
   tie and move on (the effect is too small to matter or to measure before 3 Nov).
4. **Only send what the specialist panel ranks above the online bot.** Self-play local wins have been worth nothing
   online for fight changes (part 1).
