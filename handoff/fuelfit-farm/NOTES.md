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
