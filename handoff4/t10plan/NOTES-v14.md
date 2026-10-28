# t10plan-v14 "where the 25 hitter-rounds go" (2026-10-28): v4o2 + leave judged every turn + bail alone

Base: **v4o2** (`zips/e1foco-t10plan-v4o2.zip`). Zip `zips/e1foco-t10plan-v14.zip` (sha256 in `zips/SHA256SUMS`), diff
`src/t10plan-v14_vs_v4o2.diff` (279 lines: verdict.h, main.cpp x4 anchors, params.h). Everything under `P_V14` (params.h); with
`P_V14 0` the build is v4o2. Nothing before r30 (`P_V14_R`), no init printf. Draft, shop and micro untouched. One stdout line per
firing: `[v14-leave] r= ch= foes= allies= ratio= hp= n=` and `[v14-bail] r= ch= hp= rem=`.

## 1. Measurement: every champion-round r30-150 in one bucket (an/state14.py, 160 online games vs ranks 5-20, replays_c37)

Buckets, first match wins: dead; hit (a damaging step on a camp); fight (dealt or took champion damage); flee (moved with
champion damage in the previous 4 rounds); reward (standing within 2 of a group in reward_available); recall (the still rounds
before a teleport, or within 3 of the own spawn); still; walk_camp (moved closer to the group of the next camp it hits within 40
rounds); walk_home (moved closer to the own spawn); walk_other. Champion-rounds per game (5 champions x 121 rounds = 605, minus
unspawned slots).

| bucket | rival (v4o2 batch) | us v4o2 | diff | rival (kvvl batch) | us kvvl | diff |
|---|---|---|---|---|---|---|
| hit | 109.0 | 84.1 | **+25.0** | 112.9 | 85.1 | **+27.8** |
| fight | 38.1 | 33.5 | +4.6 | 40.3 | 35.4 | +4.9 |
| flee | 25.1 | 19.2 | +5.9 | 27.3 | 21.1 | +6.1 |
| reward wait | 35.5 | 31.3 | +4.2 | 37.9 | 36.2 | +1.7 |
| recall / at base | 40.6 | 45.4 | -4.8 | 43.2 | 36.7 | +6.5 |
| standing still | 24.1 | 15.2 | +8.9 | 22.6 | 13.6 | +9.0 |
| walking to a camp target | 129.3 | 124.9 | +4.4 | 125.4 | 130.6 | -5.2 |
| walking home | 24.9 | 29.1 | -4.2 | 22.3 | 32.6 | -10.3 |
| walking elsewhere | 83.5 | 79.1 | +4.4 | 83.4 | 86.2 | -2.8 |
| **dead** | **34.4** | **79.6** | **-45.3** | **29.3** | **64.0** | **-34.7** |

Per alive champion-round (v4o2 batch, rival 510 / us 462 alive rounds a game): hit 21.4% vs 18.2%, fight 7.5 vs 7.3, flee 4.9 vs
4.2, reward 7.0 vs 6.8, recall 8.0 vs 9.8, still 4.7 vs 3.3, walk_camp 25.4 vs 27.0, walk_home 4.9 vs 6.3, walk_other 16.4 vs 17.1.
No alive bucket is 25 rounds apart; the rival does not wait less, walk less or recall less. **The one bucket is dead: 45 (v4o2
batch) / 35 (kvvl batch) champion-rounds a game**, i.e. 0.9 / 0.7 more deaths a game at 60 rounds of respawn each (dead rounds per
death 60.2-60.5 on both sides). The 45 dead rounds at the rival's hit share (21%) are 10 hitter-rounds; the other 15 are the lower
hit share of our alive rounds (18.2% vs 21.4%), which goes with the same thing: a champion walks back from the spawn after each
death (walk_camp 27% vs 25%, recall 9.8% vs 8.0%).

Travel between consecutive engagements of one champion (different groups): rival 10.9 a game, 23.1 rounds / 11.8 tiles (median
16 / 9); us 7.3 a game, 31.0 rounds / 14.2 tiles (median 24 / 12); 1.96 vs 2.18 rounds per tile. Transitions under 10 rounds 27% vs
11%. Engagements (one champion, one group) 13.2 vs 9.7 a game with the same length (8.5 vs 8.4 rounds, 8 hits). Target choice 10
rounds before the first hit: the rival takes the nearest alive group 26% of the time (us 30%), hp of the group taken 2308 vs the
nearest 2549 (us 2202 / 2707), 8.3 tiles away vs 6.0 to the nearest (us 9.0 / 7.1): the same choice.

### Deaths r30-150 (v4o2 batch; kvvl batch in brackets)

| | rival | us |
|---|---|---|
| deaths / game | 0.65 [0.66] | **1.54** [1.39] |
| killed by champions (>= 50% of the hp lost in the last 10 rounds) | 65% = 0.42/game | 73% = **1.12/game** [92% = 1.28] |
| killed by a camp | 0.23/game | **0.41/game** [0.11] |
| champion-killed, 5 rounds before: allies within 6 / foes within 6 | 1.21 / 2.29 | **0.83 / 2.74** |
| champion-killed, allies within 6 = 0 / 1 / 2+ | 26 / 35 / 38% | **44** / 34 / 21% |
| champion-killed, foes within 6 = 1 / 2 / 3+ | 18 / 35 / 44% | 7 / 33 / **57%** |
| champion-killed, dealt champion damage in the last 10 rounds | 321 (0 dealt 12%) | 362 (0 dealt 7%) |
| champion-killed, rounds moving toward the own spawn in the last 8 | 2.9 | 3.4 |
| camp-killed: hp 5 rounds before / allies within 6 / was hitting | 52% / 1.61 / 44% | 48% / 0.79 / 52% |
| by champion | Vendetta .16 Vesper .12 Ryth .11 HoR .11 Marcella .06 | Ryth .35 Marcella .33 Vesper .33 HoR .29 Vendetta .17 |

Trajectory of our 90 champion-killed deaths (mean): r-20 hp 94%, 0.9 foes within 6, 1.1 allies; r-15 88%, 1.6 foes; r-10 74%,
2.5 foes, 1.0 allies; r-5 44%, 2.8 foes, 0.8 allies; r-1 8%. In 97% of them 2+ foes were within 6 at some point in the 25 rounds
before, on average 16 rounds before the death with us at 90% hp (>= 60% hp in 92%, >= 8 rounds before in 95%). The rival's 34
look the same (2+ foes 17.6 rounds before at 83% hp) but there are a third as many: it carries 1.2-1.6 allies within 6 into the
contact against our 0.8-1.1, and it leaves (its first-contact leave rate was already measured at 42% vs our 15% in verdict.h).

**Conclusion: the missing hitter-rounds are deaths.** The held "stay" verdict of v4o2 (verdict.h: judged once at first contact,
usually 1 foe, ratio fine) is never judged again; the 2nd and 3rd rival arrive over the next 10 rounds and the champion trades
down to 0 while dealing 360 damage. Second, smaller: 0.41 vs 0.23 deaths a game to a camp, farming alone (0.79 allies) at half hp
(P_BAIL_PCT 12 and P_RESERVE_PCT -60 let a champion start and keep hitting a group it cannot afford).

## 2. v14 (diff `src/t10plan-v14_vs_v4o2.diff`)

1. **`pv::v14_judge`** (verdict.h), called every turn from r30 right after `pv::verdict` (not on the spawn, not while capturing
   before a recall): with 2+ foes within 6 (not on their spawn) and `power_ratio` < 0.80 (`P_V14_RATIO`, the 0.8 of the verdict.h
   measurement: below it we lose 40% and win 4%), or alone (no ally within 6) under 50% hp (`P_V14_LOWHP`) with any foe within 6
   and ratio < 1, the verdict becomes "leave" and holds like a first-contact leave (ends `P_PV_GAP` rounds after the last foe within 8;
   flips back only when the ratio climbs to 1.875, i.e. allies arrived). v7r judged again only when another foe entered and at 0.60.
2. **A v14 leave walks home**: recall when nobody can interrupt (`rsafe`, > 6 from the spawn), else hit what is in reach, `flee()`
   (toward the spawn; `safe_step` could stand still out of reach), shoot back. The bcf engage (`tgt->d <= 5`) is gated while a v14
   leave holds.
3. **`[v14-bail]`**: farming with no ally within 6 under 25% hp (`P_V14_BAIL`; v4o2 bails at 12%) drops the group for 30 rounds and
   leaves (the existing bail path).

## 3. Local check (70 maps x 2 sides vs kvvl, cambc 4.0.0; an/state14.py and an/shop13.py on dec37/v4o2k, dec37/v14k; an/gems14.py; an/v14lines.py)

| | v4o2 | **v14** |
|---|---|---|
| wins vs kvvl | 80/140 | **91/140** |
| `[v14-leave]` a game: r30-150 / r150-300 / r300-600 / r600+ | - | 2.49 / 3.91 / 8.30 / 21.0 (median ratio 42, hp 78%; foes 2 in 61%, 3+ 28%; allies 0 in 49%) |
| `[v14-bail]` a game | - | 0 (never fires: see below) |
| leave episodes (one per champion per 20 rounds) r30-150 / r150-600 | - | 1.75 / 7.15 a game; died within 20 rounds 14% / 11%; reached the spawn within 20 rounds 31% / 32% |
| deaths r30-150 a game: total / champion-killed / camp-killed | 1.01 / 0.63 / 0.38 | **0.86 / 0.52 / 0.34** |
| champion-rounds dead r30-150 (rival kvvl) | 52.9 (45.6) | **43.1** (34.0) |
| champion-rounds hitting r30-150 (rival kvvl) | 97.1 (99.2) | **99.6** (102.9) |
| deaths <= r600 / whole game | 4.58 / 10.51 | **3.64 / 8.22** |
| gold captures r30-150 a game / hitter-rounds per capture / bodies | 4.28 / 20.6 / 1.58 | 4.36 / 20.5 / 1.60 |
| captures <= r600 | 27.5 | 27.8 |
| gems submitted r300 / r600 / end (rival end) | 118 / 263 / 790 (718) | 120 / **269** / **835** (702) |
| final round | 1299 | 1331 |

The lever moves in the direction measured: 0.15 fewer deaths a game in r30-150 (10 fewer dead champion-rounds, +2.5 hitting),
0.9 fewer deaths to r600 and 2.3 fewer over the game, with captures and the hitting phase unchanged; +11 games, outside the +-7
noise of this bench. Locally against kvvl the dead gap was only 7 rounds (53 vs 46), so the local ceiling of the rule is small; the
online gap is 45.

Why the 25% bail never fires (an/campd analysis in NOTES): our camp-killed champion goes 84% -> 59% -> 36% -> 22% -> 9% hp in the
last 10 rounds (0.5 foes within 6, hitting until r-3): a strong group kills from full in 7-8 rounds; at 25% there are 1-2 rounds
left and P_BAIL_PCT 12 takes it. The affordable test (`squad_needed` with hp + 60% of max hp, `P_RESERVE_PCT -60`) is judged only
before the first hit.

## 4. v14b: v14 + the alone-affordability check while engaged (diff `src/t10plan-v14b_vs_v14.diff`, zip `zips/e1foco-t10plan-v14b.zip`)

From r30, farming with no ally within 6 and nobody else claiming the group, every round while engaged: `squad_needed(rem, str, dps,
hp - 25% max hp)` > 1 drops the group for 30 rounds and leaves (`[v14-camp] r= ch= hp= rem= str= need=`); bail backstop 35%
(`[v14-bail]`); not on a monolith / jackpot run. The bench was interrupted by a container restart at 110 games and the missing 30
were played afterwards with the same binaries (an/gems14.py reads wins from the replays).

| | v4o2 | v14 | v14b |
|---|---|---|---|
| wins vs kvvl | 80/140 | **91/140** | 86/140 |
| `[v14-camp]` / `[v14-bail]` a game (r30-150) | - | 0 / 0 | 1.00 / 0.18 (6.4 / 1.4 whole game) |
| deaths r30-150: total / champion-killed / camp-killed | 1.01 / 0.63 / 0.38 | 0.86 / 0.52 / 0.34 | 0.90 / 0.54 / 0.36 |
| champion-rounds dead / hitting r30-150 | 52.9 / 97.1 | 43.1 / 99.6 | 45.1 / 95.8 |
| deaths <= r600 / whole game | 4.58 / 10.51 | 3.64 / 8.22 | 3.81 / 8.71 |
| gold captures r30-150 / hitter-rounds per capture | 4.28 / 20.6 | 4.36 / 20.5 | 4.38 / 19.9 |
| captures <= r600 | 27.5 | 27.8 | 27.7 |
| gems r300 / r600 / end (rival end) | 118 / 263 / 790 (718) | 120 / 269 / 835 (702) | 116 / 259 / 820 (742) |

The camp rule fires once a game in the window but the camp-killed deaths do not move (0.36 vs 0.34): the champion that dies to a
camp at r30-150 loses 84% -> 9% in 10 rounds, and at the round the formula first says "no" it is already inside the group's range;
what the rule does drop are groups the champion would have finished (hitting rounds 99.6 -> 95.8, -5 games). **Deliverable: v14**
(`zips/e1foco-t10plan-v14.zip`). The camp deaths need the decision before the first hit (the afford reserve of `squad_needed`,
P_RESERVE_PCT -60), which is a v4o2 farm rule outside this task's "remove the bucket" scope; left as a follow-up.

Tools: `an/state14.py DIR [--index] [--pertype]` (buckets, travel, engagements, target choice, deaths with context), `an/v14lines.py TAG`
(`[v14-*]` lines from the local replays' stdout), `an/gems14.py TAG BOT` (wins, gems r300/r600/end, deaths, captures from replaydump).
