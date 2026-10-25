# fuelfit — farm section (choose_target, step_towards, engage_camp, refresh_groups)

Exact optimisations over `handoff/fuelfit/fuelfit-a1.zip` (kvvl + o01-o05). Every patch here was checked with the
unlimited-fuel bench (`--fuel-quantum 2000000`, 40 maps x 2 sides vs 6 rivals = 80 games, `tools/same.py` -> `differ 0`).

## Patches (`opts/`, apply in name order after the integrator's series)

| patch | what | exactness argument | 80-game check |
|---|---|---|---|
| `o41_ctfield.py` | choose_target: ONE export of the reached mask (bitboard, packed bits) and ONE export of the distance field instead of `is_set` (47) + `get` (41) per group tile; per-group tile indices computed once per game (groups are fixed after `init_groups`) | exports are tile-exact copies (bench: 0 mismatches of 10000); same min over the same tiles | differ 0 |
| `o42_stepsnap.py` | step_towards (tpc / dash / stuck scans), `mp_dash_hole_step` ring scan, `isle_escape` landing scan read from static exported snapshots (`BitSnap`, `DistSnap`) instead of one SDK import per tile; `vblock` copied only when the volley ring writes to it | snapshots taken after the last write to the field they copy; loops keep order, bounds and strict `<` tie-breaking; `isle_escape` still iterates `pocket.positions()` (its order decides ties); the 8-tile stuck scan uses the snapshot only when a scan above already paid for it | differ 0 |

`o06`-style numbering in the original development copies: o41 = o06, o42 = o08 (comments say so).

## The finding that changes the design: fuel is instruction metering

Bench (`a1b`, big_world / corridors):

| C++ work | fuel |
|---|---|
| trivial loop, 10 000 iterations (volatile sink) | 100 011 (~10 per iteration) |
| scanning 1 681 exported bits | 26 055 |
| own C++ BFS over 10 000 tiles | > 1 000 000 (the turn dies) |
| zero-filling a 20 KB `std::vector` (DistSnap on 100x100) | ~10 000 |
| one `printf` line | 568 |

Engine-side search is native and cheap by comparison: `distance_field::compute` ~3.4 fuel per visited tile (3 367 on 41x41,
30 616 on 100x100). So: never move an engine search into C++ (an "o09" that did this was exact but 30x dearer and killed
round 1 on big maps); every snapshot buffer must be a function-level static (a first o42 with per-call vectors was exact
but MORE expensive than the imports it replaced); count loop iterations when fitting the worst turn.

## SDK prices measured (per call)

bitboard: is_set 47, set 75, copy/or/not/and-not 500-660, is_empty 62-196, count 196, positions(16) 716,
export_linear_buffer 190 (packed bits LSB-first, index y*w+x, size (w*h+7)/8), draw_chebyshev 505-660, ctor+set 267, copy+clear 298.
distance_field: get 41, compute(200) 3.4k (41x41) / 30.6k (100x100), compute_to 1.1k-3.9k when the destination is reached
(exhaustive = full compute when it is not), export_linear_buffer 457 (41x41) / 2536 (100x100), next_moves_from 848.
champion: health/attack_range/position/can_move/can_cast 44-76, abilities() 71, abilities()[k].is_ready 616 (!), cooldown 175,
consumables() 7, consumables.count 32, gem_count 49, is_alive 49. camp: health/max_health/strength/position 45-48 each
(one `detail::sdk_camp` read gives all four: 19), is_visible 52, spawn_position 6, state 32, group.camps() 7.
vision: visible_tiles_into 299, champion_tiles 566, camp_tiles 251. read_sm 26, my_roster 1.2-1.7k, vis_champions (o01 copy) 2.7-4.1k.
`sdk_costs.md`'s camp_health 1997 was not reproduced.

## Engine search rules (verified, useful for exactness arguments)

* `distance_field::compute` = 8-neighbour BFS; a wall blocks only its own tile (a diagonal step past a wall corner is
  allowed); tiles at distance == max_distance are reached, farther ones are not. All 40 maps, every champion's position,
  rounds 3-60: 3 182 comparisons, 0 mismatches in distances and in the visited mask (alternative corner rules fail).
* `next_moves_from(p)` = the neighbours with distance d(p)-1, in compass order from north with north = (0,+1):
  (0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1). 4 569 samples, 0 mismatches.
* The visited mask of an early-stopped `compute_to` could NOT be replicated (expansion order unknown: 12 candidate
  orders/stop rules all mismatch). Exact code may read a `compute_to` field only at tiles whose distance is below the
  destination's distance (those layers are complete whatever the stop point). This is what makes a bounded
  `compute_to(..., max_distance = bound)` exact when every read is of a distance < bound.

## Profile (80 games, 108 270 champion turns, unlimited fuel, `tools/prof_fp.py`)

farm section p50 10k, p90 22.5k, p99 52.5k, p99.9 72.5k, max 213k (base a1). On heavy farm turns choose_target_impl
~24k mean when it runs (compute 11k + scoring loop 8.5k + pd_gd 4.6k before o41) and step_towards ~12k (its heavy
cases: `mp_dash_hole_step`'s exhaustive compute_to when the goal is unreachable through holes, the jammed-corridor second
compute_to, `isle_escape` 190k before o42). Numbers after o41+o42 in RESULTS (farm thread) once the profile run ends.

## Tools (`tools/`)

`prof_fp.py SRC` turns the FP/FP_SCOPE no-ops into a per-section/per-scope fuel meter (`[fpt]` heavy turns, `[fph]`
histograms); `fph_pct.py RESDIR` percentiles per scope; `fpt_agg.py RESDIR [THR]` composition of heavy farm turns;
`ct_prof.py SRC` sub-scopes inside choose_target_impl / step_towards (on top of prof_fp.py; anchors match a1+o41+o42).

## Added 2026-10-25 (all 80/80 byte-identical over fuelfit-a1 + o41 + o42)

| patch | what | exactness argument |
|---|---|---|
| `o43_dashcap.py` | `mp_dash_hole_step`: the hole-route `compute_to` bounded by `max_distance = here - P_MP_DASHHOLE` (it was exhaustive, ~30k on 100x100, whenever we are unreachable through the holes) | reached within the bound -> same BFS distance; not reached -> the original returned 0 at `hh > here - P_MP_DASHHOLE` with no side effect; every later read is at a distance < hh (complete layers) |
| `o44_dist.py` | `dist()` in 32-bit arithmetic (vec2::chebyshev_distance promotes to int64: 50 fuel per call; ~6 calls per group per choose_target, loops in step_towards and the fight code) | coordinates < 2^15, same max of the same absolute differences |
| `o45_ctrev.py` | choose_target: (A) per-group REVERSE fields (one `compute` from the group's tiles over static walls, once per game: 42k on corridors/12 groups .. 551k on big_world/24; then `is_set` + `get` at pos per group, 1.2-3.3k per call) replace the forward search from pos (3.4k-30k every retarget turn); the original path stays for the turns before all fields exist and when pos is a static-block tile. `P_FARM_PD_PER_TURN` (default all) lets the integrator spread the precompute over turns: same decisions, different fuel schedule. (B) scoring loop: claimers counted in one pass over the claim slots, per-group constants (doorstep / half-map booleans, recall cycle) once per game, `walk()` computes the straight-line distance only when used | (A) undirected unit grid with fixed walls: d(pos, group) = min over tiles of the forward BFS = the group field at pos; verified identical on 6 maps, 287 positions, 0 mismatches. (B) same integers and the same double expressions in the same order |

Profile after o41..o45 pending (RESULTS in the farm thread). `o46_groupvis.py` (refresh_groups / near_camps read one exported vision board) is in its 80-game check.

| `o46_groupvis.py` | refresh_groups: "any tile of the group visible" from ONE export of `s.vis` (static buffer) and per-game tile indices instead of `is_set` per tile (100-300 imports every turn); near_camps: the engine vision board `tv` exported once instead of `is_set` per camp spawn tile | same bits read after the board was written (s.vis assigned once per turn before refresh_groups; tv filled in near_camps); `any` is order-independent. 80/80 identical. Needs BitSnap from o42 |

Profile after o41..o45 (80 games, 108 270 turns): farm section p90 20k -> 17.5k, p99 52.5k -> 35k, p99.9 70k -> 47.5k,
turns >= 50k 1401 -> 87; choose_target p99 32.5k -> 17.5k, p99.9 50k -> 27.5k; step_towards unchanged (p99.9 37.5k;
heavy-turn mean 15.5k = exhaustive compute_to 7.9k + dash-holes 9.6k + move 4.1k + tpc 4.8k); turn total p90 62.5k -> 57.5k,
p99 90k -> 82.5k. The remaining choose_target cost is the pure C++ scoring loop (~500 fuel per group). Exact pieces plateau
around farm p99.9 ~45k: the 25k goal needs decision changes (K nearest groups scored, one path search per turn, isle_escape
every 10 rounds), judged by strength, never by fuel.

## o5x: decision-changing caps (NOT exact), judged by strength against the base on the same games

Paired comparison: same 80 games (40 maps x 2 sides, 6 deterministic rivals rotating), base = a1 (== a1+o41..o46).
`pair.py` net = wins gained - lost over the games whose result changed, bar = 2*sqrt(changed); `vstat.py` a14 = state at
r300 (gems, gold, deaths, monster damage; +0.637 for the base), `divloc.py` = games whose timelines differ.

| patch | rule | 80 games | verdict so far |
|---|---|---|---|
| `o51_onesearch.py` | step_towards: when the first field does not reach us, no second ("corridor jammed") search this turn (P_ONE_SEARCH) | 11 games differ, 3 results changed, net -3 (bar 3.5); a14 +0.637 -> +0.612 | doubtful: 240 more games running |
| `o52_ctk.py` | choose_target scores only the P_CT_K = 12 nearest groups by walking distance (+ current target + leader's group) | 57 differ, 22 results changed, net +2 (bar 9.4); a14 +0.637 -> +0.827, gems300 +19.7 -> +26.0, gold300 +256 -> +321 | neutral-to-positive on strength, cuts the scoring loop on 24-46-group maps; 240 more games queued |
| `o53_isle10.py` | isle_escape plans at most once every P_ISLE_EVERY = 10 rounds off the mainland | 2 differ (first divergence r502+), 0 results changed | neutral: safe to take |

Fuel effect is not measured here (unlimited-fuel bench); the integrator's worst-turn fit decides what each cap buys.

## o48_warmup.py (over b6 = o01-o11, o21-o26, o31-o33, o41-o47; anchors on the integrator's reanchored o46)

The once-per-game farm tables out of the first playing turn: `bool farm_warmup(State& s, int quota)` builds, for up to
`quota` groups per call, the shared per-group tile index list (used by o41 and o46, which each built their own) and the
o45 scoring constants; returns true when every group is done. Call it from the init steps after stage 3 (needs groups,
centres, spawn_pd). Any farm code needing the tables before that completes them on the spot (`farm_warmup_now`), so the
decision never depends on when they were built. BitSnap/DistSnap now keep an uninitialised heap array (`new T[n]`, the
export overwrites every byte) instead of a zero-filled std::vector: the first load of a 20KB distance snapshot no longer
costs ~10k. Measured (b6wm, unlimited fuel): first group 1.5-2.6k (includes the table allocation), then ~450-520 per group
(corridors 12 groups 68 tiles: 1483 + 5753; big_world 24/92: 1923 + 10775; islands 46/118: 2613 + 20171).
Price to budget: 2.5k + 600 per group. 80/80 byte-identical replays (b6 vs b6+o48).

## o49_warmup2.py (over b6 + o48)

More once-per-game work into `farm_warmup`'s first call: share_pow's std::pow table (o05; 303 fuel per pow, up to 18 on the
first choose_target calls) is global and filled in the warm-up; `tank_bits(s)` and the roster handles are learned there;
the reverse-field objects (`s.pd_rf` / `s.pd_rv`, N bitboard constructors at 251 each) are allocated there instead of in
farm_pd_ready's first call (the 12k "first field"). `my_roster` returns a const reference (it copied the vector on every
call, also in vcarry_on). Exact: same values computed earlier / not copied. 2/2 games identical to b6; 80-game check running.
Per-game price of the first farm_warmup call: 18 pows 5.4k + roster/tank_bits ~2.5k + N x ~260 for the field objects + 2.5k
tables; later calls 600 per group.

## o49 check: 80/80 byte-identical replays (b6 vs b6+o48+o49), 10-25 00:48 UTC.

## o5x on the integrator's b10 (10-25 01:10-01:50 UTC; unlimited fuel; 56 far = far.sh, 80 near = subq)

| patch | far 56: differ / results changed / net | far wins | far a14 | near 80: changed / net | near a14 |
|---|---|---|---|---|---|
| b10 | - | 36/56 | -0.106 | - | +0.437 |
| o52 K=12 | 14 changed, net +4 (bar 7.5) | 40/56 | +0.131 | 10 changed, net +2 | +0.643 |
| o51+o52+o53 | 16 changed, net +2 | 38/56 | +0.137 | 11 changed, net +3 | - |
| o51 | 2 changed, net 0 | 36/56 | | | |
| o53 | 0 changed | 36/56 | | (earlier: 2 differ, 0 results) | |

Verdict: **o52 yes** (positive on every panel so far: 80 a1 +2/22, 80 b10 +2/10, 56 far +4/14, a14 and gems300 up each
time; it is the piece that cuts the scoring loop on 24-46-group maps). **o53 neutral** (take it for the cap). **o51 drop**
(nothing to gain, doubtful on 160 earlier games).

## Far-map profile of b10 (12 games: islands, ambush, big_world, great_wall, expanse, fracture x rTop1 x 2 sides)

tools/prof_fp48.py + ct_prof48.py (48 scopes; [fpt] also on tribute >= 25k), fpt_st.py (heavy turns by section),
fph_tot.py (turns by total cost from the [fph] histograms). b10: 15438 turns, 286 >= 77.5k (1.85%), 132 >= 87.5k.

Finding 1 (fixed by **o54_pdsched.py**, exact): choose_target_impl runs only every few rounds per champion on far maps, so
the o45 reverse fields (one per call) took 250-500 rounds to warm up, and every call meanwhile paid the forward field AND
one reverse field: ct:compute 30-35k from r11 to r300 (present on 95-100% of heavy farm turns). o54: choose_target never
computes a reverse field (uses them only once all exist, else the forward field); the warm-up runs at the end of every
playing turn that did not pay the forward field and is not a tribute walk (dead, fight, approach-cached, recall turns), one
field per turn, fixed rule, no fuel read. init_wait (o47) keeps computing them on the idle round.

Finding 2 (fixed by **o55_stskip.py**, exact): step_towards off the mainland (big_world (71,80) after a dash over holes,
ambush's moated room, islands) ran two exhaustive searches (live block, then static+camps; 26-30k each on 100x100)
before isle_escape's third. Both block sets contain s.static_block, so with every goal on the mainland neither can reach
us: skipped. The mainland bitboard (component of our spawn over static walls) is global now (g_mainland), computed in the
first o54 warm-up slot or by isle_escape as before.

Finding 3 (**o56_islecache.py**, exact, small): isle_escape's landing scan (<= 80 pocket tiles x 24 landings x wall
check, ~30k C++) is built once per island and kept with the pocket; the pocket field runs before the goal field so an
island over P_ISLE_MAX returns before the exhaustive search. isle still costs ~55k when it runs (the goal field is
exhaustive by nature: dest unreachable) -> o53 (every 10 rounds) stays useful.

After o54+o55(+o56), same 12 games: turns >= 77.5k 286 -> 156 (1.0%), >= 87.5k 132 -> 57; heavy farm turns (farm section
>= 30k and total >= 76k) 1153 -> 547; ct:compute mean on them 21k -> 4.4k. 12/12 replays identical to b10 (profile builds).
Exactness (b10 vs b10+patch, byte-identical replays): o54 80/80 near + 56/56 far; o55 80/80 near + 56/56 far; o54+o55+o56 80/80 near + 56/56 far. All three integrated in the integrator's b12 (commit fbc87a3) with o52+o53.

What remains on far maps (mean on heavy farm turns after o54-o56, present%): step_towards 25.6k (99%: goal search st:ct1
9k, dash holes 11.5k when present, isle 55k on 5%), choose_target 24k (74%: ct:score 15k -> o52), engage_camp 15k (15%,
max 88k: one outlier to look at), and outside farm: play_turn start "init" section 23k on 27% (cf_observe /
br_static_step: recall thread), post-sweep 15.5k on 51% and log 12.8k on 22% (pelea / integrator), shop 25k on 31% of
tribute turns. Tribute turns: step_towards 24k (st:ct1 8k, dash holes 9k), not 44k: the 44k figure was isle_escape.

Final check (01:50 UTC): o52 on top of o54+o55+o56 (f52) gives exactly the same 56 far + 80 near games as o52 on b10 (0
replays differ), so the three exact pieces are exact also with the cap on; strength as o52: far net +4/14, wins 40/56,
a14 +0.131; near net +2/10, a14 +0.643. b12 (integrator) = b10 + o52-o56.

b14 (integrator: b12 + o35 altar fields 1/turn on big maps + o57 first playing round by init cost model) vs b10 on the
same panels (02:15 UTC): far 56: 15 changed, net +5 (bar 7.7), wins 36 -> 41/56, a14 -0.106 -> +0.029 (below o52's
+0.131: the later first round on 100x100 maps costs early state, not results); near 80: 15 changed, net +9 (bar 7.7,
passes), WR 0.66 -> 0.78, a14 +0.437 -> +0.700. vs o52-on-b10: far +1/11, near +7/11.

## First playing turn on 100x100 maps (b16, 02:40-03:00 UTC; prof_fp48 printing every turn <= r8; 8 games)

Measured (per champion, unlimited fuel): ambush r4 131-162k, big_world r5 155-171k, islands r4 104-126k, road_of_riches
r4 102-113k. Parts: choose_target 38-57k (forward field 26-31k + o41 read-out 6-16k + K-cut/score), recall section
26-31k (cr_return_walk computes the home field on its first call: recall thread), br_static altar field 23-27k (o58 moves
it), step_towards 16-40k (goal search 11-14k, dash-hole search 14-20k, move 8k), fight 6k, decide 3.6k, post 6.5k.
On islands/road_of_riches the forward field is cheap (6k: few passable tiles) but choose_target still paid 20-25k outside
the scoring loop: unreach() asked s.mp_dashholes.is_empty() (SDK, ~200) for every unreachable group, twice per call.

- **o59_unreach.py** (exact): is_empty() once per choose_target call. Saves 7k (big_world) to 11-17k (islands) per call,
  every call, not only the first.
- **o60_pdprefill.py** (exact): the forward field from the spawn and its read-out are computed in init_wait (idle round),
  into the per-position cache; the first turn finds `cached` and skips both (keyed by position: a moved champion misses
  and pays as before). The first playing turn is marked as having paid its field so the o54 warm-up slot skips it
  (otherwise the end-of-turn reverse field, which profiles in the "log" section, ate the saving).
  First turn after o59+o60: ambush 100-130k, big_world 116-131k, islands 91-108k, road_of_riches 87-99k.
  Idle round cost grows by ~14k (prefill 32k minus one reverse field less).
What is left on the first turn that is not the engine's goal search: recall home field 26-31k and altar field 23-27k
(both static: idle-round material), then ambush/big_world would be ~50-80k. Exactness runs (56 far + 80 near vs b16) in
progress.
Exactness of o59+o60 over b16 (03:08 UTC): 56/56 far and 80/80 near byte-identical replays. Both are in the integrator's
b18 (with o58 altar fields and o62 recall home field on the idle round): first playing turn on 100x100 ambush 97k,
big_world 100k, islands 91k, starvation 89k, road_of_riches 81k; what is left there is the engine's goal searches of
the first step_towards. b18 is the night's candidate; the PC's Judge 2 decides between b15/b16/b18.

## b15 (chosen base, no idle-round work): first playing turn on the 14 far maps (05:50-06:10 UTC, unlimited fuel)

Per champion (min..max over the 5), b15 -> b15+o59+o63:

| map | groups | first turn b15 | +o59+o63 | choose_target | forward field | recall (home field) | altar field (init-sec) | step_towards |
|---|---|---|---|---|---|---|---|---|
| ambush | 12 | r2 108-139k | 108-139k | 39k -> 39k | 26k | 26k | 0 | 16-40k |
| big_world | 24 | r3 155-171k | 150-164k | 56k -> 50k | 31k | 31.5k | 27.5k | 9-28k |
| starvation | 14 | r2 101-124k | 98-120k | 37k -> 34k | 21.6k | 21.8k | 0 | 17-35k |
| expanse | 24 | r3 96-108k | 91-103k | 34k -> 28k | 11.8k | 12k | 15.7k | 8-21k |
| fracture | 28 | r3 99-106k | 93-101k | 39k -> 33k | 15k | 15.3k | 11.4k | 7-15k |
| islands | 46 | r3 87-111k | 78-95k | 42k -> 28k | 6k | 6.4k | 10.7k | 7-19k |
| road_of_riches | 51 | r3 92-100k | 83-90k | 39k -> 30k | 6k | 6.6k | 10.4k | 5-10k |
| pilgrimage | 23 | r3 88-96k | 83-92k | 32k -> 28k | 11.8k | 12.1k | 11.4k | 7-17k |
| lanes | 42 | r3 78-86k | 70-79k | 33k -> 25k | 5.7k | 0 | 12.1k | 7-15k |
| concentrated_wealth | 11 | r2 75-92k | 75-92k | 24k -> 24k | 13.5k | 13.9k | 0 | 12-22k |
| great_wall | 17 | r3 68-80k | 64-76k | 23k -> 19k | 4.5k | 5k | 9.8k | 5-18k |
| shortcut | 21 | r3 76-81k | 71-76k | 24k -> 19k | 3.9k | 4.4k | 10.1k | 5-9k |
| split | 32 | r3 74-79k | 67-73k | 29k -> 23k | 3.8k | 4.3k | 9k | 6-12k |
| rows | 9 | r2 52-61k | 52-61k | 17k -> 17k | 7k | 7.2k | 0 | 6-11k |

- **o63_gdonce.py** (exact, after o52): each group's walking distance computed once per call (pre-sized static array)
  and reused by the scoring loop; with o59 it takes 5-13k off choose_target on 24-51-group maps, on every call (islands
  42k -> 28k, road 39k -> 30k, lanes 33k -> 25k). On 9-12-group maps it is neutral (+0.1-0.2k).
- What remains in choose_target's own code on big maps: 3k exports, ~4k claim reads, ~200 per group in walk() (dist +
  cache checks), 4-6k scoring of the 12 nearest. The forward field (engine) is 4-31k and cannot be prefilled on b15
  (no idle-round work: the PC rejected b19); the field export writes 65535 for unreached tiles (probe), so the reached
  mask is not needed for the read-out (190 fuel: not worth a patch).
- The same static engine fields appear three times on the first turn of big maps: forward field (farm), home field
  (recall: cr_return_walk's first call, 26-31k on ambush/big_world/starvation) and an altar field (o35, 10-27k). The
  recall and altar ones are not needed on the first turn (no gems); moving them to the o54 end-of-turn slot (one static
  field per turn that did not pay a forward field and is not a tribute) would take 26-59k off it with no init work.
- Boundary view (budget 85,984 per round, ~172k for two): a turn that always spills by a wide margin and emits its
  action at the end is as deterministic as one that fits. The risky first turns are the ones within ~2k of a multiple:
  lanes 78-86k and concentrated_wealth 75-92k straddle 86k; islands 87k and pilgrimage 88k sit just over it; big_world
  171k sits just under 172k. After o59+o63: lanes 70-79k and split/shortcut/great_wall clear of it; islands 78-95k and
  road 83-90k now straddle it, pilgrimage 83-92k too: cutting the home field (26-31k) as well is what moves ambush,
  starvation, expanse, fracture, islands, pilgrimage, road under 86k together.
Exactness over b15 (06:10 UTC): o59 56/56 far + 80/80 near; o59+o63 56/56 far + 80/80 near byte-identical replays.
Both add no init work and no idle-round work: safe for the b15 line.

## o64_staticq.py (over b15 + o59 + o63; 06:30 UTC): the end-of-turn slot becomes the static-work queue

One engine field per turn that did not pay the forward field and is not a tribute walk, fixed order: recall home field
(cr_home_prepare, factored out of cr_return_walk, which keeps the on-demand compute as fallback) > altar fields
(br_static_step, no longer at the start of play_turn; br_plan keeps its cached/uncached paths) > mainland (o55) >
reverse group fields (o45). cr_capture_extra asks for the home walk only when it can change the answer (hp < 90% or
gold >= 90: cr_optional_value is false otherwise whatever the walk; the counters are under the same condition).
First playing turn, b15 -> b15+o59+o63+o64 (per champion, 14 far maps): big_world 155-171k -> 91-105k, ambush 108-139k
-> 82-113k, starvation 101-124k -> 77-99k, islands 87-111k -> 62-78k, expanse 96-108k -> 64-76k, fracture 99-106k ->
67-74k, road 92-100k -> 66-74k, pilgrimage 88-96k -> 61-69k, lanes 78-86k -> 58-67k, concentrated_wealth 75-92k ->
62-79k, great_wall 68-80k -> 50-62k, shortcut 76-81k -> 57-62k, split 74-79k -> 55-60k, rows 52-61k -> 45-54k.
Ten of the 14 maps are now under 86k for every champion on the first turn; big_world stays over (forward field 31k +
step_towards 9-28k + base), ambush and starvation straddle it (step_towards 16-40k: dash champions pay the dash-hole
search).
Exactness over b15 (06:35 UTC): b15+o59+o63+o64 56/56 far + 80/80 near byte-identical replays (same.py differ 0).
So the queue never changes a decision: br_plan's uncached path before the altar fields are ready, the home field
computed later and the recall fallback all give the same answers as computing them on the first turn. o64 is exact
and adds no init work and no idle-round work: safe for the b15 line (and b24hp/b26).

## o65_fieldreuse.py (over b15 + o59 + o63 + o64): the two goal fields of a walking turn kept and reused -- CLOSED 10-25 10:30 UTC, NOT ADOPTED

Script kept in opts/not-adopted/ (v6; exact by construction, v1-v3 verified 56/56 far + 80/80 near, v4-v6 not re-verified
because none saves fuel where it matters). Do not apply it.

What it does: step_towards' goal field (roots = goal tiles, walls = s.blocked, stopped at our tile, 14-17k on ambush,
13-17k starvation, 8-9k big_world) and mp_dash_hole_step's field (holes open, 14-20k / 13-16k / 4-8k) are kept in State
and reused when every read is provably the same: (a) each tile that became a wall has cached distance >= D, (b) each tile
that stopped being a wall has all 8 neighbours at cached distance >= D - 1, (c) no changed tile inside the goal mask
(roots unchanged); exhausted bounded searches are a negative cache (D = B + 1); after a pass with changes the kept walls
become today's. The rule is right (0 mismatches cached vs fresh in 240k checks, x65n) and holds on 60-72% of walking
searches overall (x65p) -- but almost only on quiet turns.

Six versions, full-game profiles against e64 (14 far maps vs rTop1, unlimited fuel, prof_fp48 + ct_prof48, cmpprof.py):
- v1-v4 (bitboard copies of roots/walls, == compares, 8 reads per freed tile): turns >= 86k WORSE (ambush 25 -> 54/43,
  big_world 26 -> 59/53). Microbenchmark on 100x100 (x65m): bitboard copy 480 (alloc ~280 + import 199), == 222,
  xor/and/not/shift ~390, is_empty 217, count 215, positions(n) ~450 + 45n, is_set 61, get 64, camp_tiles 384,
  champion_tiles 1007, compute_to minimum 2.9k (+~3.4 per visited tile), std::vector of 1250 B 1.7k. On 41x41 about half.
  => a reuse test that copies anything costs more than the field it saves on short searches, and the miss path is what
  heavy turns pay.
- v5 (no copies: s.blocked double-buffered by swap with a generation counter, goals keyed by object pointer, one shared
  wall diff per step_towards, lazy goal bbox): heavy turns no longer worse (ambush 25/25, starvation 7/7, big_world
  26/31) but not fewer; common turns +0.4-0.9k.
- v6 (chebyshev rings keyed by centre+radius from engage, cf, bank, group, fight, cassi: zero-cost compare): same
  picture (ambush 25/25, big_world 26/33, 77.5k: ambush 79/75, big_world 74/81).
Why it cannot land (x65q, miss reasons printed per turn on 6 heavy maps): of 87 turns >= 86k, 58 come from the camp
probe (goals = g.mask & ~probe_seen & ~s.blocked, a new mask each turn; keyable but see next), 11 from the bank ring,
11 from cf. Among keyed checks on printed (heavy/early) turns the dominant miss is "a tile that became a wall has
cached distance < D" (ambush 116 of ~170, big_world 328): a teammate stepping ahead of us in the group walk. Target
changes (key miss) are the next. Hits happen on quiet solo walks, which never reach 86k. Each failed check on a churn
turn costs == 222 + xor 394 + count 215 (+ positions and reads when listed) ~0.8-1.5k: exactly the turns at the
boundary pay it. Relaxing the rule to "only the tiles we read keep their distance" needs a chain of reads down to the
changed tile (50-100 gets = 3-6k) and a delicate proof: not worth it.

Also measured (x65q, same 6 maps): the exact skip of the hole search "no crossable hole within Chebyshev hole_bound of
the goal bbox" applies to 3% (ambush, fracture, islands), 6% (starvation), 22% (big_world), 38% (lanes) of the hole
searches and to 1/42, 0/13, 1/45, 0/12, 7/31, 2/3 of the heavy turns: not a lever. The hole route IS the behaviour on
ambush/starvation/fracture (reached and used on 56-82% of calls) and pure cost on big_world/lanes (reached 0/766,
0/168: ~11k per call for nothing) and islands (30/952).

Correction (integrator, 08:46 UTC): in b15 and everything above it fuel_ok() is a stub returning true (o07), so the
`fuel_ok(40000)` in front of the hole step decides nothing: the hole search always runs and its cost is deterministic.
The first-turn chaos on ambush/starvation/big_world is the total turn cost against 86k (overflow pushes actions to the
next round), not a fuel-read branch.

Lesson (fuelfit): an exact cache only pays if the MISS path costs ~0 and the misses are not the heavy turns. Here the
heavy turns are the misses by construction (group walks, new targets).

## First-turn forward field of choose_target: NOT reducible exactly on ambush/starvation (10-25 09:00 UTC, x65r bench build)

Per group on the first turn (r2/r3), Chebyshev distance vs walking distance, and the forward field's distance histogram,
14 far maps. A bounded search (max_distance B) reads the same as the full one only if (1) the P_CT_K = 12 nearest
groups are reached within B (their exact distances feed the K-cut and the scores) and (2) every unreached group is
provably beyond the cut: without a dash it is skipped either way; with a dash unreach() prices it 2*cheb+10, so
2*cheb+10 > cut is needed, else the fake value enters the scoring where the true one would not. s.target and the lead
group are scored beyond the cut and must be reached too. With n <= 12 groups there is no cut and every group needs its
true distance, unreachable ones included (which cannot be told from "beyond B" without the full search).
| map | n | unreachable | bound needed | area needed / full | B from 1.3*cheb+6 |
| ambush | 12 | 2 | 107 (all groups) | 6680 / 7542 | 100 (fails: unreachable groups) |
| starvation | 14 | 0 | 160-180 | 4387-5484 / 5667 | 85 (fails) |
| big_world | 24 | 4 | 83-88 | 4523 / 8780 | 72 (fails, close) |
| expanse | 24 | 0 | 63 | 3751 / 6134 | 78 (ok) |
| fracture | 28 | 2 | 78-89 | 1755 / 3386 | 55 (fails) |
| pilgrimage | 23 | 0 | 107-152 | 1685-2533 / 2583 | 48 (fails) |
| lanes | 42 | 0 | 37 | 1163 / 2597 | 54 (ok) |
Chebyshev underestimates the walking distance 1.5-2x on these maps (ambush: farthest group cheb 74, walking 107), so
the bound cannot be guessed; a short bound plus the full search costs more than today. big_world would save ~48% of
31k with the right bound, ambush 11%, starvation 3-22%: no exact lever on the three chaos maps. Not pursued.

## r8-r9 peak on 11 of 14 far maps (integrator's kidbg profile): the periodic re-choice

e64pf full-game profile, r6-r10 turns >= 60k: the dominant scope is choose_target (15 = 27-46k, forward field 23 =
13-30k) on ambush r8 (all five, 77-95k), starvation r8 (71-90k), big_world r9 (vendetta 86k), fracture r9 (62-66k),
road_of_riches r9 (68-71k), expanse r9, islands r9, concentrated_wealth r8. It is `refresh` in the farm step:
round - s.target_round >= P_E_RETARGET = 6 (the first choice is r2 on 12-14-group maps, r3 on the others), no fuel
involved. The champion has moved since r2, so the per-position cache misses and the reverse fields (o54: one static
field per cheap turn, 26k each on 100x100; farm_pd_done needs all 12-24) are not complete until ~r15-r27: the full
forward field is paid again. Exact ways out: none found. Two reverse fields per warm-up turn would put r3-r7 (60-75k
with the 22-26k warm-up field already inside) over 86k; a hybrid read (reverse fields where they exist, Chebyshev
bound for the rest) needs cheb > cut for every missing group, which the 1.5-2x gap defeats; the r2 forward field kept in
s.pdf is from another position (triangle bounds only). Non-exact option for the stall thread: defer the periodic
refresh until farm_pd_done (the re-choice then costs ~1.5k instead of 26-31k, but it happens at r15-r27 instead of
r8-r9: a decision change, judge by strength). The other half of those turns is the first step_towards to the new target
(goal field + hole field, 20-35k): the same two engine searches as on the first turn.

## o66_readout.py (over b15 + o59 + o63 + o64; 09:15 UTC): mask-free read-out, direct scans on big maps (EXACT)

(a) choose_target's read-out of the forward field (o41) tested the reached bit of every group tile before taking its
distance (24-51 groups x ~30 tiles: 8-13k, scope 25). The export holds 65535 on every unreached tile, larger than any
reached distance, so the reached mask export and the bit tests go: one min() per tile; -1 when the min is 65535.
(b) step_towards' dash scan (25 tiles) and tp-crystal scan (29 tiles) took three snapshots first (o42: s.blocked,
s.visited, s.df = 2.9k on 100x100, ~840 on 41x41). On maps of 4096+ tiles they now read directly: an unreached tile
reads 65535 and never beats bestd, so the reach test is implied; the wall test only for a tile that would win. Same
candidates in the same order, same best. Smaller maps keep the snapshots.
Profile e66p vs e64pf, r2-r12, common turns: ambush -578 per turn (first turn 113k -> 108k), big_world -796 (105k ->
101k), expanse -658, fracture -783, road -440, great_wall -386, others -30..-350. (The e66p profile build's scope 38
anchor did not match, so 38 is folded into 16/37 there; the totals are right.)
Exactness of o66 over b15 (b15+o59+o63+o64+o66; 09:45 UTC): far 56/56 and near 80/80 byte-identical replays.

## o67_rfdefer.py (over b15 + o59 + o63 + o64 (+ o66); 10:00 UTC): the periodic target refresh waits for the reverse fields (NOT EXACT)

Decision change, for the PC to judge by strength against b27. `refresh` (round - target_round >= P_E_RETARGET = 6) is
skipped while the reverse fields are not complete (farm_pd_done) and we are not on the tile the cached distances were
measured at, only on maps of P_RF_DEFER_AREA = 4096 tiles or more (near maps play exactly as before: the forward field
costs 4-14k there) and only while round < P_RF_DEFER_R = 60. A missing or expired target chooses at once, as before.
Profile e67p vs e64pf (14 far maps, r2-r40, unlimited fuel): choose_target turns >= 15k on r4-r12 per map 3-5 -> 0
(islands 1: an expired target); max turn r4-r12 ambush 95k -> 86k, starvation 90k -> 80k, big_world 91k -> 88k,
road 71k -> 62k, split 53k -> 41k, concentrated_wealth 67k -> 60k; turns >= 77.5k over r2-r40: ambush 27 -> 14,
starvation 16 -> 6, big_world 23 -> 16, others unchanged. Behaviour: the first periodic re-choice happens when the
reverse fields are complete (~r15-r27 on 12-24-group maps) and costs ~1.5k instead of 26-31k; until then the champion
keeps its first target unless it expires. Near 80 (must be byte-identical: the rule is off below 4096 tiles) and far 56
(strength vs rTop1/rD) running.
o67 runs (10:50 UTC, unlimited fuel, P_RF_DEFER_AREA = 4096): near 80 and far 56 vs b15: 132 of 136 replays
byte-identical, including both sides of ambush, big_world, starvation, expanse (far) and corners (near): the deferred
refresh confirms the target the r8-r9 refresh would have chosen, so only the fuel changes there. The 4 that differ are
the A side of fracture (61x71 = 4331 tiles, 28 groups): b15 won all four by ~1030-340 gems; e67 lost two (936-1199 vs
rD, 781-1070 vs rF) and won two narrowly. Keeping the first target ~30 rounds on fracture is a real loss, and its forward
field is only 15k. => P_RF_DEFER_AREA raised to 5000 (fracture excluded; 100x100 and 80x80 maps and corners kept).
With that default every game of this panel is byte-identical to b15 (far 56 re-run in progress to confirm): on this
panel o67 behaves as an exact piece; the PC's 800 games decide whether other big maps change.
o67 with P_RF_DEFER_AREA = 5000 (11:20 UTC): far 56/56 byte-identical to b15 (near 80 were identical already below the
threshold). On this panel o67 only removes fuel (r8-r9 re-choice field on ambush, big_world, starvation, expanse).

## o68_nohole.py (over b29; 10-25 12:30 UTC): the dash-hole shortcut (mapplan rule 5) off, or only when it does not split the group (NOT EXACT)

Why near fight maps lose (user: c19 b27 -41 gems/game on near maps; reverse_spiral -337, rushbait_v2 -228). Local, b27 vs
kvvl (bot/mgwp), 2 maps x rTop1/rD/rF/mV10d x 2 sides, normal fuel: reverse_spiral b27 0/8 (kvvl 7/8). Same target
(group 9) in both, but in b27 Heart of Ruin and Vesper die at r24-r27 in every game (17 deaths <= r100 over 8 games,
kvvl 0), so the camp is cleared at r100+ instead of r74: 7 gems / 0 gold at r100 over 8 games (kvvl 366 / 1528).
Per-round trace (status line every round): HoR and Vesper take the dash-hole shortcut (mp_dash_hole_step; HoR dash r7
(10,10)->(7,9), Vesper r9) through the middle, alone, next to the enemy spawn (spawn-to-spawn path 1), and the enemy
Marcella kills them; Marcella and Ryth walk the long way (y = 21) like all four of kvvl. kvvl never did this: the step is
behind fuel_ok(40000) and, as the stall thread then measured, kvvl's mp_find_dashholes gate (P_DHFUEL_NEED) said no
3699 times and yes 0 on 26 near maps, so kvvl had no dash holes at all; b15+ computes them in init (o06) and fuel_ok is
a stub. b27 with the step off (b27nh): reverse_spiral 7/8, 0 deaths <= r100, net gems +2238 (b27 -2770, kvvl +887);
rushbait_v2 7/8, +2859 (b27 +506, kvvl +642).
P_MP_HOLE: 0 = never (kvvl's behaviour everywhere, near and far: proposed as b31), 1 = as b29, 2 = only when no ally
without a dash (by name: ren, vesper, vendetta, heart) claims the same target group while we farm (dash_bits +
hole_splits_group, ~30 fuel per call). Panels running on b29 / b29h0 / b29h2: 6 losing maps (reverse_spiral,
rushbait_v2, fragment, hooks, contest, starfish) x 6 rivals x 2 sides, far 56, near 80.

## o68 panels (10-25, local, b29 = b28 + o66 + o67; h0 = P_MP_HOLE 0, h2 = P_MP_HOLE 2)

| panel | b29 | b29h0 | b29h2 |
|---|---|---|---|
| 6 losing near maps x 6 rivals x 2 sides (72) | 45 (+19984 gems, 83 deaths <= r100) | 53 (+28533, 48) | 49 (+24053) |
| far 56 (rTop1, rD, both sides) | 43 (+13822, 18) | 40 (+9764, 16) | 48 (+15546, 13) |
| near 80 (one game per map and rival) | 55 (+17615, 52) | 56 (+21853, 40) | 58 (+22201, 43) |
| sum (208) | 143 | 149 | 155 |

reverse_spiral in the 72: b29 0/12, h0 6/12, h2 4/12; contest/fragment/hooks identical (no dash champion uses a hole
there). h0 loses the far maps where the hole routes are real shortcuts (road_of_riches 3->1, shortcut 4->3, islands
3->2, concentrated_wealth 4->3). Recommended P_MP_HOLE 2 (integrator: b31 = h0, b32 = h2, b33 = h2 + small holes).

kvvl on the same near 80: 54/80 (+23271, 41 deaths). b29 vs kvvl: 33 outcome flips (+17 -16), no identical game
(different lineages). Near maps where b29h2 is still below kvvl (kvvl 2/2, h2 1/2): elkring (gems 330 vs 1320),
gem_fields (243 vs 905), gemfight (191 vs 1648; b29 2/2, an h2 regression), lost_world (647 vs 1797), rows (148 vs
1094), split (273 vs 680), stampede (480 vs 1280), starfish (30 vs 983), swirl (-39 vs 1927). Where h2 beats kvvl:
broken_curve, corridors, eight, expanse, fracture (kvvl 0/2), fragment, interlock, islands (kvvl 0/2), quadrants,
shortcut, pilgrimage. Results: farm container /tmp/claude-0/ff/ws/res/{kvvl,b29,b29h0,b29h2}_n80; table by
`python3 -I cmpbots.py "" kvvl_n80 b29_n80 b29h2_n80`.

## Gem macro: how the top 10 take gem-bearing elk groups (10-25, coordinator's request)

Data: 40 top-10 near-map games (analysis/top10-micro-1023/dec300, rounds <= 150) vs b29 and kvvl on the near 80
panel above (replays decoded with capkind_light.dump; scripts in the farm container /tmp/claude-0/ff/gem: capseq.py,
elkdetail.py, ebmetrics.py, openshape.py, perteam.py, trace.py). A capture = the group's captureTeam switching to us.

| per game, rounds <= 150 | top 10 (40) | b29 (80) | kvvl (80) |
|---|---|---|---|
| elk+gem captures by r50 / by r150 | 0.62 / 1.70 | 0.29 / 0.86 | 0.23 / 0.74 |
| own-side elk+gem groups available (>= 15 gems) | 2.92 | 2.60 | 2.60 |
| gold-cluster captures by r50 | 0.75 | 1.35 | 1.31 |
| first capture: round, champions within 4 | r22, 3 | r25, 2 | r26, 2 |
| first capture is a gold cluster | 10/40 | 47/80 | 43/80 |
| first three captures with 3+ champions / solo | 55% / 17% | 31% / 45% | 26% / - |
| champions within 5 of the nearest own-side elk+gem group at r10 | 1.31 | 0.80 | 0.72 |
| deaths <= r100 | 0.35 | 0.65 | 0.51 |

Elk+gem captures by the top 10 arrive with 3 champions (median; 57% with 3+), arrival spread 8 rounds, first approach
to capture 55 rounds (median; the opening ones r1 -> r12-r26). From r50 on our elk capture rate matches theirs
(0.57 vs 1.08 per game between r50 and r150, with the same number of champions). The whole gap is the opening: the
top 10 open with the team on one group (elk+gem when it is the nearest rich group, else wolf+gem or a gold cluster),
capture it at r12-r26 with 3-5 champions and then spread; we open with 5 solo gold clusters (median 1 champion) and
reach the first elk group at r48-r54. Per team (perteam.py): Fish, willow best girl, :3, Shingtonwash, Claudus,
policy wonk and procless all show first captures with 3-5 champions; Mite and Trzy Kwaterki open more spread.

### o69_teamopen.py (teamopen-v1; NOT exact, judge by strength)
Until round P_TO_R (40) the first alive ally in draft order leads: its choose_target values every group for the
whole team (the dormant `pack` hook: value not shared, clear time with the roster, no "needs company" discount); the
others take the leader's claimed group x P_GROUP_W (the existing ball code, groups > 8 tiles from the leader x 0.3)
and re-choose every 3 rounds. P_TO_NEAR 1 limits it to near maps (spawn-to-spawn path < P_PF_MAX). No fuel read;
followers' extra choose_target calls in r0-r40 cost fuel on 100x100 maps (the forward field) - measure on the PC.
Two test games (elkring, hooks vs rTop1): hooks first capture elk+gem r27 with 4 champions (b29: gold cluster r23
with 2, the elk group at r90); elkring both bots send the team to the altar-held group 20 tiles away (P_HOLD 200), the
rival contests it and o69's five fight there (2 deaths) while b29's four captured it at r30. Local panel (near 80 +
far 56 vs b29) running; results below when done.

### o69 teamopen-v1: local panel vs b29 (10-25 10:15 UTC)

| panel | b29 | b29 + o69 | flips |
|---|---|---|---|
| near 80 | 55/80 (+17615 gems, 52 deaths <= r100) | 61/80 (+25457, 56) | +13 -7 |
| far 56 | 43/56 (+13822, 18) | 47/56 (+16848, 33) | +10 -6 |
| total 136 | 98 | 108 | +23 -13 (bar 2*sqrt(36) = 12) |

Near maps gained: collision, elk_arena, elkring, gem_fields, great_wall, hooks, lost_world, pilgrimage, road_of_riches,
rows, starfish, starvation; lost: boss_battle, gemfight, gold_rush, islands, packs, shortcut. Far: ambush 1->3,
starvation 2->4, pilgrimage 2->3, islands/road/split 3->4; big_world 4->3 (12 deaths <= r100), concentrated_wealth
4->3, great_wall 3->2 (10 deaths), rows 3->2. Far deaths <= r100 double (18 -> 33): the team walks together into
contested middles on 100x100 maps. If the PC confirms the far loss, P_TO_NEAR 1 keeps far maps identical to b29.

Mechanism (ebmetrics/openshape on the same near 80; top 10 for reference):

| rounds <= 150 | top 10 | b29 | b29 + o69 |
|---|---|---|---|
| first capture: round, champions within 4 | r22, 3 | r25, 2 | r29, 3 |
| first three captures with 3+ champions / solo | 55% / 17% | 31% / 45% | 50% / 27% |
| first capture is elk+gem / gold cluster | 13 / 10 of 40 | 9 / 47 of 80 | 39 / 20 of 80 |
| elk+gem captures by r50 / r150 | 0.62 / 1.70 | 0.29 / 0.86 | 0.51 / 1.09 |
| gold-cluster captures by r50 | 0.75 | 1.35 | 0.79 |
| group gems captured <= r150 per game | 80.5 | 106.7 | 85.4 |
| deaths <= r100 per game | 0.35 | 0.65 | 0.70 |

The opening now has the top-10 shape (3 champions on the first group, elk first); early group gems drop (fewer solo
gold clusters) while the final gem margin rises (+25457 vs +17615 over 80 games); early deaths do not fall yet (the
team fights where it meets the rival). Package for the PC: /mnt/project-files/bundles/teamopen-v1-b29.zip (644d36e9,
b29 src + o69, P_TO 1 / P_TO_R 40 / P_TO_NEAR 0). Variants worth a PC run: P_TO_NEAR 1; P_TO_R 25.

### o69 v1 over b32 (10-25 11:00 UTC; local b29h2 = b32 up to the inert P_MP_HOLE_SMALL 0)

| panel | b32 | b32 + o69 v1 | flips |
|---|---|---|---|
| near 80 | 58/80 (+22201, 43 deaths <= r100) | 58/80 (+26645, 52) | +11 -11 |
| far 56 | 48/56 (+15546, 13) | 44/56 (+16002, 34) | +7 -11 |

Over the stronger base v1 is neutral on near maps and loses far maps (deaths <= r100 13 -> 34: big_world 12, great_wall
10, fracture/shortcut 4). Part of the gain seen over b29 was reverse_spiral-type games that o68 already fixes. Not a PC
candidate as is. Losses with v1 (gemfight, packs, gold_rush, trace.py): the leader's team valuation sends the whole team
to the rich centre group (gemfight 78 gems, 12 camps; packs 28; gold_rush) and two champions die there at r27-r45.
v2 = P_TO_OWN 1: the team valuation applies only to groups on our side (closer to our spawn by P_TO_OWN_D 2); the top
10's elk captures are own-side in 47 of 68. v2 panel over b32 running.

### o69 v2 (P_TO_OWN 1) over b32 (10-25 11:55 UTC) - line closed

| panel | b32 | b32 + o69 v2 | flips |
|---|---|---|---|
| near 80 | 58/80 (+22201, 43 deaths <= r100) | 59/80 (+27000, 42) | +13 -12 |
| far 56 | 48/56 (+15546, 13) | 42/56 (+14198, 35) | +7 -13 |

Own-side-only valuation removed the centre-group losses (gemfight, packs, gold_rush now even or won) but the near
panel stays neutral and the far panel loses the same games as v1 (big_world 12 deaths <= r100, great_wall 10,
concentrated_wealth 4->1, islands 4->2): on 100x100 maps the team arriving together does not stop the early deaths.
Over b29, b32 and 408 local games the opening ball moves the mechanism (first capture with 3 champions, elk first) but
not the result: neutral on near maps, negative on far maps. teamopen is NOT a PC candidate (P_TO_NEAR 1 would only be a
neutral near-only piece). The opening shape of the top 10 is therefore a correlate, not the lever; the deaths that
separate us (0.65-0.70 vs 0.35 per game by r100, 62-71% of them with an enemy within 3) are fight outcomes.
